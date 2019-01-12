from datetime import datetime
from eth_tester import PyEVMBackend, EthereumTester
from web3 import (
    Web3,
    HTTPProvider,
    IPCProvider,
    WebsocketProvider,
    EthereumTesterProvider,
)
from web3.middleware.fixture import construct_fixture_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from .. import store
from ..exceptions import SolidbyteException
from ..logging import getLogger
from ..networks import NetworksYML
from ..utils import to_path_or_cwd
from .middleware import SolidbyteSignerMiddleware

log = getLogger(__name__)

TEST_BLOCK_GAS_LIMIT = int(6.5e6)
ETH_TESTER_TYPES = ('eth_tester', 'eth-tester', 'ethereum-tester')


class Web3ConfiguredConnection(object):
    """ A handler for dealing with network configuration, and Web3 instantiation.
        It loads config from the project's networks.yml and tries to use that.
        Fallback is an automatic Web3 connection.
    """

    def __init__(self, connection_name=None, no_load=False):
        self.name = connection_name
        self.config = None
        self.networks = []
        self.web3 = None

        project_dir = to_path_or_cwd(store.get(store.Keys.PROJECT_DIR))
        self.yml = NetworksYML(project_dir=project_dir, no_load=no_load)

        if no_load is not True:
            try:
                self.yml.load_configuration()
            except FileNotFoundError:
                log.warning("networks.yml not found")

    def _load_configuration(self, config_file=None):
        """ Load configuration from the configuration file """
        return self.yml.load_configuration(config_file)

    def _init_provider_from_type(self, config):
        """ Initialize a provider using the config """
        if not config.get('type'):
            raise SolidbyteException("Invalid configuration.  type must be specified")

        if config['type'] == 'ipc':
            return IPCProvider(config.get('file') or config.get('url'))
        elif config['type'] == 'websocket':
            return WebsocketProvider(config.get('url'))
        elif config['type'] == 'http':
            return HTTPProvider(config.get('url'))
        elif config['type'] in ETH_TESTER_TYPES:

            # Get genesis params with our non-default block gas limit
            params = PyEVMBackend._generate_genesis_params(overrides={
                'gas_limit': TEST_BLOCK_GAS_LIMIT,
            })

            # Init EthereumTester with the py-evm backend
            tester = EthereumTester(backend=PyEVMBackend(
                    genesis_parameters=params
                ),
                auto_mine_transactions=True
            )

            # Init the web3.py provider
            provider = EthereumTesterProvider(ethereum_tester=tester)

            """ We need to mess with the provider middleware to set the chain_id/net_version.
            EthereumTesterProvider currently uses fixtures with default values to provide things
            like responses to net_version or eth_syncing.

            Ref: https://github.com/ethereum/web3.py/blob/master/web3/providers/eth_tester/middleware.py#L262-L273 # noqa: E501
            """

            # These definitions are taken from the ref above and cannot be imported
            fixture_middleware = construct_fixture_middleware({
                # Eth
                'eth_protocolVersion': '63',
                'eth_hashrate': 0,
                'eth_gasPrice': 1,
                'eth_syncing': False,
                'eth_mining': False,
                # Net
                'net_version': str(int(datetime.now().timestamp())),
                'net_listening': False,
                'net_peerCount': 0,
            })

            # It's a setter/getter property that returns a tuple. Use a list so we can replace.
            middlewares = list(provider.middlewares)

            i = 0
            for m in middlewares:
                log.debug(m.__name__)
                if m.__name__ == 'fixture_middleware':
                    middlewares[i] = fixture_middleware  # Replace with our own
                    break
                i += 1

            # Set the new middlewars for the provider
            provider.middlewares = middlewares

            return provider
        else:
            raise SolidbyteException("Invalid configuration.  Unknown type")

    def get_web3(self, name=None):
        """ return a configured web3 instance """
        if name == self.name and self.web3:
            return self.web3

        log.debug("Creating new web3 object.")

        self.web3 = None

        if name and (not self.yml.network_config_exists(name) and name != 'test'):
            raise SolidbyteException("Provided network '{}' does not exist in {}".format(
                    name,
                    self.yml.config_file,
                ))
        elif name and self.yml.network_config_exists(name):
            # Allow network 'test' even if it isn't defined
            if name == 'test' and not self.yml.network_config_exists(name):
                conn_conf = {
                    'type': ETH_TESTER_TYPES[0],
                    'autodeploy_allowed': True,
                }
            else:
                conn_conf = self.yml.get_network_config(name)

            success = False
            if conn_conf.get('type') == 'auto':
                self.web3 = Web3()
                success = self.web3.isConnected()
            else:
                provider = self._init_provider_from_type(conn_conf)
                success = provider.isConnected()
                self.web3 = Web3(provider)

            # Stupid hack because eth_tester has chain_id == 1 hardcoded.  It's checked in
            # deploy.objects.Deploy so SB knows if it has to prompt for a password and unlock.
            if conn_conf.get('type') in ETH_TESTER_TYPES:
                self.web3.is_eth_tester = True
            else:
                self.web3.is_eth_tester = False

            if not success:
                log.error("Connection to {} provider failed".format(conn_conf.get('type')))
                raise SolidbyteException("Unable to connect to node")

        else:
            log.warning("No network provided.  Attempting automatic connection.")
            from web3.auto import w3 as web3
            self.web3 = web3

        self.name = name

        # Setup gasPrice strategy
        self.web3.eth.setGasPriceStrategy(medium_gas_price_strategy)

        # Add our middleware for signing
        self.web3.middleware_stack.add(SolidbyteSignerMiddleware, name='SolidbyteSigner')

        return self.web3
