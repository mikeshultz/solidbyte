""" Very simple module we can use to store session-level data.  This saves certain things from
    having to be passed through dozens of functions or objects.
"""
from enum import Enum
from typing import Optional, Any, Dict


class Keys(Enum):
    # The account decrypt passphrase that should be session-wide.
    DECRYPT_PASSPHRASE = 'decrypt'

    # The directory with the Ethereum secret store files
    KEYSTORE_DIR = 'keystore'

    # The project directory.  Probably pwd.
    PROJECT_DIR = 'project_dir'

    # The name of the network being used as defined in networks.yml
    NETWORK_NAME = 'network_name'


STORAGE: Dict[Keys, Any] = {}


def defined(key: Keys) -> bool:
    """ Check if the key is defined and in STORAGE """
    return key in STORAGE


def get(key: Keys) -> Optional[Any]:
    """ Get the value stored for the key """
    return STORAGE.get(key)


def set(key: Keys, val: Any) -> Optional[Any]:
    """ Set the value of the key and return the new value """
    STORAGE[key] = val
    return val
