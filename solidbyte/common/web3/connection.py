import sys
import yaml
from os import getcwd
from pathlib import Path
from attrdict import AttrDict
from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
from web3.gas_strategies.time_based import medium_gas_price_strategy
from ...common.exceptions import SolidbyteException
from ...common.logging import getLogger
from .middleware import SolidbyteSignerMiddleware

log = getLogger(__name__)

class Web3ConfiguredConnection(object):
    """ A handler for dealing with network configuration, and Web3 instantiation.
        It loads config from the project's networks.yml and tries to use that.
        Fallback is an automatic Web3 connection.
    """

    def __init__(self, connection_name=None):
        self.name = connection_name
        self.config = None
        self.networks = None
        self.web3 = None

        try:
            self._load_configuration()
        except FileNotFoundError:
            log.warn("networks.yml not found")

    def _load_configuration(self, config_file=None):
        """ Load configuration from the configuration file """

        if config_file is None:
            config_file = Path(getcwd()).joinpath('networks.yml')
        elif type(config_file) == str:
            config_file = Path(config_file).expanduser().resolve()

        if not config_file or not config_file.exists():
            log.warn("Missing config_file")
            return

        try:
            with open(config_file, 'r') as cfile:
                self.config = yaml.load(cfile)
                self.networks = list(self.config.keys())
        except Exception as e:
            log.exception("Failed to load networks.yml")
            raise e

    def _network_config_exists(self, name):
        """ Check and see if we have configuration for name """
        log.debug("_network_config_exists({})".format(name))
        try:
            self.networks.index(name)
            return True
        except ValueError:
            return False

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
        else:
            raise SolidbyteException("Invalid configuration.  Unknown type")

    def get_web3(self, name=None):
        """ return a configured web3 instance """
        web3 = None

        if name and not self._network_config_exists(name):
            raise SolidbyteException("Provided network '{}' does not exist in networks.yml".format(name))
        elif name and self._network_config_exists(name):
            conn_conf = self.config[name]

            success = False
            web3 = None
            if conn_conf.get('type') == 'auto':
                web3 = Web3()
                success = web3.isConnected()
            else:
                provider = self._init_provider_from_type(conn_conf)
                success = provider.isConnected()
                web3 = Web3(provider)

            if not success:
                log.error("Connection to {} provider failed".format(conn_conf.get('type')))
                raise SolidbyteException("Unable to connect to node")

        else:
            log.warn("No network provided.  Attempting automatic connection.")
            from web3.auto import w3 as web3

        # Setup gasPrice strategy
        web3.eth.setGasPriceStrategy(medium_gas_price_strategy)

        # Add our middleware for signing
        web3.middleware_stack.add(SolidbyteSignerMiddleware, name='SolidbyteSigner')

        return web3