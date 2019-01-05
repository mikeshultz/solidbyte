""" Very simple module we can use to store session-level data.  This saves certain things from
    having to be passed through dozens of functions or objects.
"""
from enum import Enum
from typing import TypeVar

T = TypeVar('T')

STORAGE = {}


class StoreKeys(Enum):
    DECRYPT_PASSPHRASE = 'decrypt'
    KEYSTORE_DIR = 'keystore'


class Store:
    @staticmethod
    def defined(key: StoreKeys) -> T:
        """ Get the value stored for the key """
        return key in STORAGE

    @staticmethod
    def get(key: StoreKeys) -> T:
        """ Get the value stored for the key """
        return STORAGE.get(key)

    @staticmethod
    def set(key: StoreKeys, val: T) -> T:
        """ Set the value of the key and return the new value """
        STORAGE[key] = val
        return val
