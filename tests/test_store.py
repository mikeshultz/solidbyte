""" Tests for Store object """
from solidbyte.common.store import Store, StoreKeys


def test_store():
    """ test Store """
    PASSPHRASE = 'asdf1234'
    Store.set(StoreKeys.DECRYPT_PASSPHRASE, PASSPHRASE)
    assert PASSPHRASE == Store.get(StoreKeys.DECRYPT_PASSPHRASE)


def test_store_module():
    """ test that storage is the same across modules. The only reason this might change is if Python
        changes.
    """
    from .storemodule import get_passphrase

    PASSPHRASE = 'asdf12345'
    Store.set(StoreKeys.DECRYPT_PASSPHRASE, PASSPHRASE)
    assert PASSPHRASE == get_passphrase()
