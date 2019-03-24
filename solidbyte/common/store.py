""" Very simple module we can use to store session-level data.  This saves certain things from
    having to be passed through dozens of functions or objects.

    *This is not fully implemented project wide yet.  Currently experimental.*
"""
from enum import Enum
from typing import Optional, Any, Dict


class Keys(Enum):
    """ Enum defining storage keys """

    DECRYPT_PASSPHRASE = 'decrypt'  #: The account decrypt passphrase that should be session-wide.
    KEYSTORE_DIR = 'keystore'  #: The directory with the Ethereum secret store files
    PROJECT_DIR = 'project_dir'  #: The project directory.  Probably pwd.
    NETWORK_NAME = 'network_name'  #: The name of the network being used as defined in networks.yml


STORAGE: Dict[Keys, Any] = {}


def defined(key: Keys) -> bool:
    """ Check if the key is defined and in STORAGE

    :param key: (:code:`Keys`) The key to look for
    :returns: (:code:`bool`) If the key is defined in storage
    """
    return key in STORAGE


def get(key: Keys) -> Optional[Any]:
    """ Get the value stored for the key

    :param key: (:code:`Keys`) The key of the value to return
    :returns: (:code:`Any`) The value of the key
    """
    return STORAGE.get(key)


def set(key: Keys, val: Any) -> Optional[Any]:
    """ Set the value of the key and return the new value

    :param key: (:code:`Keys`) The key of the value to return
    :param val: (:code:`Any`) The value to set
    :returns: (:code:`Any`) The value of the key
    """
    STORAGE[key] = val
    return val
