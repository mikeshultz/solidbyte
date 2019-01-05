import pytest
from attrdict import AttrDict
from ..deploy import Deployer, get_latest_from_deployed
from ..common.utils import to_path_or_cwd
from ..common.web3 import web3c
from ..common.metafile import MetaFile
from ..common.networks import NetworksYML
from ..common.exceptions import SolidbyteException, DeploymentValidationError
from ..common.logging import getLogger

log = getLogger(__name__)


class SolidbyteTestPlugin(object):

    def __init__(self, network_name, web3=None, project_dir=None):
        self.network = network_name
        self._web3 = None
        if web3 is not None:
            self._web3 = web3

        self._project_dir = to_path_or_cwd(project_dir)
        self._contract_dir = self._project_dir.joinpath('contracts')
        self._deploy_dir = self._project_dir.joinpath('deploy')

    def pytest_sessionfinish(self):
        # TODO: There was something I wanted to do here...
        pass

    @pytest.fixture
    def contracts(self):
        if not self._web3:
            self._web3 = web3c.get_web3(self.network)
        network_id = self._web3.net.chainId or self._web3.net.version
        d = Deployer(self.network, project_dir=self._project_dir)
        contracts_meta = d.deployed_contracts
        contracts_compiled = d.source_contracts
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
        if not self._web3:
            self._web3 = web3c.get_web3(self.network)
        return self._web3


def run_tests(network_name, args=[], web3=None, project_dir=None, account_address=None):
    """ Run all tests on project """

    yml = NetworksYML(project_dir=project_dir)

    # Use default account if none was specified
    if not account_address:
        mfile = MetaFile(project_dir=project_dir)
        account_address = mfile.get_default_account()
        if not account_address:
            raise DeploymentValidationError("Default account not set and no account provided.")

    log.debug("Using account {} for deployer.".format(account_address))

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

        deployer.deploy()

    elif deployer.check_needs_deploy() and not (
            yml.network_config_exists(network_name)
            and yml.autodeploy_allowed(network_name)):

        raise DeploymentValidationError(
            "Deployment is required for network but autodpeloy is not allowed.  Please deploy "
            "your contracts using the `sb deploy` command."
        )

    return pytest.main(args, plugins=[
            SolidbyteTestPlugin(
                network_name=network_name,
                web3=web3,
                project_dir=project_dir,
            )
        ])
