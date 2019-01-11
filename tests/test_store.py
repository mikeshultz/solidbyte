""" Tests for Store object """
from solidbyte.common import store


def test_store():
    """ test Store """
    PASSPHRASE = 'asdf1234'
    store.set(store.Keys.DECRYPT_PASSPHRASE, PASSPHRASE)
    assert PASSPHRASE == store.get(store.Keys.DECRYPT_PASSPHRASE)


def test_store_module():
    """ test that storage is the same across modules. The only reason this might change is if Python
        changes.
    """
    from .storemodule import get_passphrase

    PASSPHRASE = 'asdf12345'
    store.set(store.Keys.DECRYPT_PASSPHRASE, PASSPHRASE)
    assert PASSPHRASE == get_passphrase()
