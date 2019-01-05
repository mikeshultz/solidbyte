""" Handle operations around networks.yml
"""
import yaml
from typing import TypeVar, Dict
from pathlib import Path
from .logging import getLogger
from .exceptions import ConfigurationError

log = getLogger(__name__)

# Typing
T = TypeVar('T')
PathString = TypeVar('PathString', Path, str)
NetworkConfig = Dict[str, Dict[str, T]]


class NetworksYML:
    """ Object representation of the networks.yml file

    Example File
    ------------
    # networks.yml
    ---
    dev:
      type: auto
      allow_test_deployment: true

    infura-mainnet:
      type: websocket
      url: wss://mainnet.infura.io/ws

    geth:
      type: ipc
      file: ~/.ethereum/geth.ipc

    test:
      type: eth_tester
      allow_test_deployment: true

    """

    def __init__(self, project_dir: PathString = None, no_load: bool = False) -> None:
        log.debug("NetworksYML.__init__(project_dir={}, no_load={})".format(project_dir, no_load))
        if project_dir is None:
            project_dir = Path.cwd()
        elif not isinstance(project_dir, Path):
            project_dir = Path(project_dir)

        self.config_file = project_dir.joinpath('networks.yml')
        self.config = None
        self.networks = []

        if no_load is False:
            log.debug("self.load_configuration()")
            self.load_configuration()

    def load_configuration(self, config_file: PathString = None) -> None:
        """ Load the configuration from networks.yml """
        log.debug("load_configuration(config_file={})".format(config_file))
        if config_file is None:
            config_file = self.config_file
        elif type(config_file) in (str, bytes):
            if type(config_file) == bytes:
                config_file = config_file.decode('utf-8')
            self.config_file = Path(config_file).expanduser().resolve()
        else:
            self.config_file = config_file

        log.debug("resolved config file to: {}".format(self.config_file))
        log.debug("type: {}".format(type(self.config_file)))

        if not self.config_file or not self.config_file.exists():
            log.warning("Missing config_file")
            return

        log.debug("Loading networks configuration from {}...".format(self.config_file))

        try:
            with open(self.config_file, 'r') as cfile:
                self.config = yaml.load(cfile)
                self.networks = list(self.config.keys())
        except Exception as e:
            log.exception("Failed to load networks.yml")
            raise e

    def network_config_exists(self, name: str) -> bool:
        """ Check and see if we have configuration for name """

        log.debug("network_config_exists({})".format(name))
        log.debug(self.networks)

        try:
            self.networks.index(name)
            return True
        except ValueError:
            return False

    def get_network_config(self, name: str) -> NetworkConfig:
        """ Return the config for a specific network """

        if not self.network_config_exists(name):
            raise ConfigurationError("Network config for '{}' does not exist.".format(name))

        return self.config[name]

    def autodeploy_allowed(self, name: str) -> bool:
        """ Check if autodeploy is allowed on this network. It must be explicitly allowed. """

        log.debug("autodeploy_allowed(name={})".format(name))

        if not self.network_config_exists(name):
            raise ConfigurationError("Network config for '{}' does not exist.".format(name))

        log.debug("self.get_network_config(name) -> {}".format(
            self.get_network_config(name)
        ))

        return self.get_network_config(name).get('autodeploy_allowed', False)
