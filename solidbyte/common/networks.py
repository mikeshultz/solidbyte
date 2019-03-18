""" Handle operations around networks.yml
"""
import yaml
from typing import Union, Any, Dict, List
from pathlib import Path
from .logging import getLogger
from .exceptions import ConfigurationError
from .utils import to_path_or_cwd

log = getLogger(__name__)

# Typing
PathString = Union[Path, str, bytes]
NetworkConfig = Dict[str, Dict[str, Any]]

# Const
ETH_TESTER_TYPES = ('eth_tester', 'eth-tester', 'ethereum-tester')


class NetworksYML:
    """ Object representation of the networks.yml file

    Example File
    ------------
    # networks.yml
    ---
    dev:
      type: auto
      autodeploy_allowed: true

    infura-mainnet:
      type: websocket
      url: wss://mainnet.infura.io/ws

    geth:
      type: ipc
      file: ~/.ethereum/geth.ipc

    test:
      type: eth_tester
      autodeploy_allowed: true

    """

    def __init__(self, project_dir: PathString = None, no_load: bool = False) -> None:

        log.debug("NetworksYML.__init__(project_dir={}, no_load={})".format(project_dir, no_load))

        project_dir = to_path_or_cwd(project_dir)

        self.config_file = project_dir.joinpath('networks.yml')
        self.config = None
        self.networks: List = []

        if no_load is False:
            log.debug("self.load_configuration()")
            self.load_configuration()

    def load_configuration(self, config_file: PathString = None) -> None:
        """ Load the configuration from networks.yml """

        if config_file is None:
            config_file = self.config_file
        elif type(config_file) in (str, bytes):
            if type(config_file) == bytes:
                config_file = config_file.decode('utf-8')
            config_file = Path(config_file).expanduser().resolve()

        self.config_file = config_file

        log.debug("resolved config file to: {}".format(self.config_file))

        if not self.config_file or not self.config_file.exists():
            log.warning("Missing config_file")
            return

        log.debug("Loading networks configuration from {}...".format(self.config_file))

        with open(self.config_file, 'r') as cfile:
            self.config = yaml.load(cfile)
            if not self.config:
                raise ConfigurationError("Unable to load networks.yml!")
            self.networks = list(self.config.keys())

    def network_config_exists(self, name: str) -> bool:
        """ Check and see if we have configuration for name """
        try:
            self.networks.index(name)
            return True
        except ValueError:
            return False

    def get_network_config(self, name: str) -> NetworkConfig:
        """ Return the config for a specific network """

        if not self.config:
            raise ConfigurationError("Unable to load networks.yml!")
        if not self.network_config_exists(name):
            raise ConfigurationError("Network config for '{}' does not exist.".format(name))

        return self.config[name]

    def autodeploy_allowed(self, name: str) -> bool:
        """ Check if autodeploy is allowed on this network. It must be explicitly allowed. """

        if not self.network_config_exists(name):
            raise ConfigurationError("Network config for '{}' does not exist.".format(name))

        return self.get_network_config(name).get('autodeploy_allowed', False)

    def is_eth_tester(self, name: str) -> bool:
        """ Check if autodeploy is allowed on this network. It must be explicitly allowed. """

        if not self.network_config_exists(name):
            raise ConfigurationError("Network config for '{}' does not exist.".format(name))

        return self.get_network_config(name).get('type') in ETH_TESTER_TYPES
