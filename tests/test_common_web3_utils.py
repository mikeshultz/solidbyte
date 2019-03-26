""" Test web3 utils """
from hexbytes import HexBytes
from solidbyte.common.exceptions import DeploymentValidationError
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
    func_sig_from_input,
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
    TX_INPUT,
    TX_FUNC_SIG,
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


def test_create_deploy_tx(mock_project):
    """ Test deploy transaction creation function """

    with mock_project() as mock:

        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        tx = create_deploy_tx(web3, ABI_OBJ_1, CONTRACT_BIN_1, {
                'from': web3.eth.accounts[0],
                'gasPrice': int(1e9),
            })
        assert tx.get('data') is not None


def test_create_deploy_tx_invalid(mock_project):

    with mock_project() as mock:

        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        # Missing web3
        try:
            create_deploy_tx(None, ABI_OBJ_1, CONTRACT_BIN_1, {
                'from': web3.eth.accounts[0],
                'gasPrice': int(1e9),
            })
            assert False, "create_deploy_tx() should fail with missing input"
        except DeploymentValidationError:
            pass

        # Missing ABI
        try:
            create_deploy_tx(web3, None, CONTRACT_BIN_1, {
                'from': web3.eth.accounts[0],
                'gasPrice': int(1e9),
            })
            assert False, "create_deploy_tx() should fail with missing input"
        except DeploymentValidationError:
            pass

        # Missing bytecode
        try:
            create_deploy_tx(web3, ABI_OBJ_1, None, {
                'from': web3.eth.accounts[0],
                'gasPrice': int(1e9),
            })
            assert False, "create_deploy_tx() should fail with missing input"
        except DeploymentValidationError:
            pass

        # Invalid bytecode
        try:
            create_deploy_tx(web3, ABI_OBJ_1, '0x', {
                'from': web3.eth.accounts[0],
                'gasPrice': int(1e9),
            })
            assert False, "create_deploy_tx() should fail with missing input"
        except DeploymentValidationError:
            pass


def test_create_deploy_tx_without_constructor(mock_project):
    """ Test deploy transaction creation function """

    with mock_project() as mock:

        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        tx = create_deploy_tx(web3, LIBRARY_ABI_OBJ_4, LIBRARY_BYTECODE_4, {
                'from': web3.eth.accounts[0],
                'gasPrice': int(1e9),
            })
        assert tx.get('data') is not None


def test_func_sig_from_input():
    assert func_sig_from_input(TX_INPUT) == TX_FUNC_SIG
