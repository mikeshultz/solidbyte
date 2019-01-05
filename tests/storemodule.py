""" A module to be imported by test_store.py """
from solidbyte.common.store import Store, StoreKeys


def get_passphrase():
    return Store.get(StoreKeys.DECRYPT_PASSPHRASE)
