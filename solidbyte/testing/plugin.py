""" The Pytest plugin for running contract tests """
import pytest
from attrdict import AttrDict
from ..accounts import Accounts
from ..deploy import Deployer, get_latest_from_deployed
from ..common.utils import to_path, to_path_or_cwd
from ..common.web3 import web3c
from ..common.exceptions import SolidbyteException
from ..common.logging import getLogger
from .gas import construct_gas_report_middleware
from .fixtures import std_tx, get_event, has_event, time_travel, block_travel

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
        """ Init the pytest plugin

        :param network_name: (:code:`str`) - The name of the network as defined in networks.yml.
        :param web3: (:class:`web3.Web3`) - The Web3 instance to use
        :param project_dir: (:class:`pathlib.Path`) - The project directory (default: pwd)
        :param keystore_dir: (:class:`pathlib.Path`) - Path to the keystore. (default:
            :code:`~/.ethereum/keystore`)
        :param gas_report_storage: (:class:`solidbyte.testing.gas.GasReportStorage`) - An instance
            of :code:`GasReportStorage` to use if making a gas report
        """

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

    @pytest.fixture(scope='session')
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

    @pytest.fixture(scope='session')
    def web3(self):
        """ Returns an instantiated Web3 object """
        return self._web3

    @pytest.fixture(scope='session')
    def local_accounts(self):
        """ Returns the local known accounts from the Ethereum keystore """
        a = Accounts(network_name=self.network, keystore_dir=self._keystore_dir, web3=self._web3)
        return a.get_accounts()

    @pytest.fixture
    def has_event(self):
        return has_event

    @pytest.fixture
    def get_event(self):
        return get_event

    @pytest.fixture
    def time_travel(self):
        return time_travel

    @pytest.fixture
    def block_travel(self):
        return block_travel

    @pytest.fixture
    def std_tx(self):
        return std_tx
