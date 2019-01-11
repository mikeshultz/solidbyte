""" A module to be imported by test_store.py """
from solidbyte.common import store


def get_passphrase():
    return store.get(store.Keys.DECRYPT_PASSPHRASE)
