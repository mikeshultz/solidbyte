""" Test web3 utils """
from hexbytes import HexBytes
from solidbyte.common.web3 import (
    web3c,
    normalize_hexstring,
    remove_0x,
    remove_0x_to_bytes,
    to_bytes,
    normalize_address,
    hash_hexstring,
    hash_string,
    create_deploy_tx,
)

from .const import (
    NETWORK_NAME,
    TEST_HASH,
    ABI_OBJ_1,
    CONTRACT_BIN_1,
    ADDRESS_2,
    ADDRESS_2_HASH,
    ADDRESS_2_NOT_CHECKSUM,
    LIBRARY_ABI_OBJ_4,
    LIBRARY_BYTECODE_4,
)

HEX_WO_0X = 'abcdef0123456789'
HEX_W_0X = '0xabcdef0123456789'
HEXBYTES = HexBytes(HEX_W_0X)


def test_normalize_hexstring():
    assert HEX_W_0X == normalize_hexstring(HEX_W_0X)
    assert HEX_W_0X == normalize_hexstring(HEX_WO_0X)
    assert HEX_W_0X == normalize_hexstring(HEX_WO_0X.encode('utf-8'))
    assert HEX_W_0X == normalize_hexstring(HEXBYTES)


def test_remove_0x():
    assert HEX_WO_0X == remove_0x(HEX_W_0X)


def test_remove_0x_to_bytes():
    assert HEX_WO_0X.encode('utf-8') == remove_0x_to_bytes(HEX_W_0X)


def test_to_bytes():
    assert HEX_WO_0X.encode('utf-8') == to_bytes(HEX_WO_0X)


def test_normalize_address():
    assert ADDRESS_2 == normalize_address(ADDRESS_2_NOT_CHECKSUM[2:])


def test_hash_hexstring():
    assert ADDRESS_2_HASH == hash_hexstring(ADDRESS_2)


def test_hash_string():
    assert TEST_HASH == hash_string(NETWORK_NAME)


# TODO: Expand on this:
def test_create_deploy_tx():
    """ Test deploy transaction creation function """
    web3 = web3c.get_web3(NETWORK_NAME)
    tx = create_deploy_tx(web3, ABI_OBJ_1, CONTRACT_BIN_1, {
            'from': web3.eth.accounts[0],
            'gasPrice': int(1e9),
        })
    assert tx.get('data') is not None


def test_create_deploy_tx_without_constructor():
    """ Test deploy transaction creation function """
    web3 = web3c.get_web3(NETWORK_NAME)
    tx = create_deploy_tx(web3, LIBRARY_ABI_OBJ_4, LIBRARY_BYTECODE_4, {
            'from': web3.eth.accounts[0],
            'gasPrice': int(1e9),
        })
    assert tx.get('data') is not None
