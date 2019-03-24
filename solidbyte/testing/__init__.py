import pytest
from attrdict import AttrDict
from ..accounts import Accounts
from ..compile import compile_all
from ..deploy import Deployer, get_latest_from_deployed
from ..common.utils import to_path, to_path_or_cwd
from ..common.web3 import web3c
from ..common.metafile import MetaFile
from ..common.networks import NetworksYML
from ..common.exceptions import SolidbyteException, DeploymentValidationError
from ..common.logging import getLogger
from .gas import construct_gas_report_middleware

log = getLogger(__name__)


class SolidbyteTestPlugin(object):
    """ Pytest plugin that provides fixtures useful for Solidbyte test scripts

    Fixtures:
        * contracts
        * web3
        * local_accounts
    """

    def __init__(self, network_name, web3=None, project_dir=None, keystore_dir=None,
                 gas_report_storage=None):

        self.network = network_name
        self._web3 = None
        if web3 is not None:
            self._web3 = web3
        else:
            self._web3 = web3c.get_web3(self.network)

        self._project_dir = to_path_or_cwd(project_dir)
        self._contract_dir = self._project_dir.joinpath('contracts')
        self._deploy_dir = self._project_dir.joinpath('deploy')
        self._keystore_dir = to_path(keystore_dir)

        if gas_report_storage is not None:
            self._web3.middleware_stack.add(
                construct_gas_report_middleware(gas_report_storage),
                'gas_report_middleware',
            )

    def pytest_sessionfinish(self):
        # TODO: There was something I wanted to do here...
        pass

    @pytest.fixture
    def contracts(self):
        """ Returns an instantiated :class:`web3.contract.Contract` for each
        deployed contract """
        network_id = self._web3.net.chainId or self._web3.net.version
        d = Deployer(self.network, project_dir=self._project_dir)
        contracts_meta = d.deployed_contracts
        contracts_compiled = d.artifacts
        test_contracts = {}
        for meta in contracts_meta:
            latest = None
            if meta['networks'].get(network_id):
                latest = get_latest_from_deployed(
                    meta['networks'][network_id].get('deployedInstances'),
                    meta['networks'][network_id].get('deployedHash')
                    )
            if latest is not None:
                abi = contracts_compiled[meta['name']].abi
                test_contracts[meta['name']] = self._web3.eth.contract(
                    abi=abi,
                    address=latest['address']
                )
        if len(test_contracts) == 0:
            raise SolidbyteException("No deployed contracts to test")
        return AttrDict(test_contracts)

    @pytest.fixture
    def web3(self):
        """ Returns an instantiated Web3 object """
        return self._web3

    @pytest.fixture
    def local_accounts(self):
        """ Returns the local known accounts from the Ethereum keystore """
        a = Accounts(network_name=self.network, keystore_dir=self._keystore_dir, web3=self._web3)
        return a.get_accounts()


def run_tests(network_name, args=[], web3=None, project_dir=None, account_address=None,
              keystore_dir=None, gas_report_storage=None):
    """ Run all tests on project

    Args:
        * network_name (:code:`str`) - The name of the network as defined in
          networks.yml.
        * args (:code:`list`) - Arguments to provide to pytest
        * web3 (:class:`web3.Web3`) - The Web3 instance to use
        * project_dir (:class:`pathlib.Path`) - The project directory (default:
          cwd)
        * account_address (:code:`str`) - Address of the deployer account
        * keystore_dir (:class:`pathlib.Path`) - Path to the keystore. (default:
          :code:`~/.ethereum/keystore`)
        * gas_report_storage (:class:`solidbyte.testing.gas.GasReportStorage`)
          - An instance if :code:`GasReportStorage` to use if making a gas
          report
    """

    yml = NetworksYML(project_dir=project_dir)

    # Use default account if none was specified
    if not account_address:
        mfile = MetaFile(project_dir=project_dir)
        account_address = mfile.get_default_account()
        if not account_address:
            raise DeploymentValidationError("Default account not set and no account provided.")

    log.debug("Using account {} for deployer.".format(account_address))

    log.info("Compiling contracts for testing...")
    compile_all()

    log.info("Checking if deployment is necessary...")

    # First, see if we're allowed to deploy, and whether we need to
    deployer = Deployer(
        network_name=network_name,
        account=account_address,
        project_dir=project_dir,
    )

    if (deployer.check_needs_deploy()
            and yml.network_config_exists(network_name)
            and yml.autodeploy_allowed(network_name)):

        if not account_address:
            raise DeploymentValidationError("Account needs to be provided for autodeployment")

        log.info("Deploying contracts...")

        deployer.deploy()

    elif deployer.check_needs_deploy() and not (
            yml.network_config_exists(network_name)
            and yml.autodeploy_allowed(network_name)):

        raise DeploymentValidationError(
            "Deployment is required for network but autodpeloy is not allowed.  Please deploy "
            "your contracts using the `sb deploy` command."
        )

    if not web3:
        web3 = web3c.get_web3(network_name)

    retval = None
    try:
        retval = pytest.main(args, plugins=[
                SolidbyteTestPlugin(
                    network_name=network_name,
                    web3=web3,
                    project_dir=project_dir,
                    keystore_dir=keystore_dir,
                    gas_report_storage=gas_report_storage,
                )
            ])
    except Exception:
        log.exception("Exception occurred while running tests.")
        return 255

    return retval
