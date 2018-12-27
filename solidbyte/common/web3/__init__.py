from web3 import Web3
from ...common.logging import getLogger
from .connection import Web3ConfiguredConnection

log = getLogger(__name__)
web3c = Web3ConfiguredConnection()


def normalize_hexstring(hexstr):
    if isinstance(hexstr, bytes):
        hexstr = hexstr.hex()
    if hexstr[:2] != '0x':
        hexstr = '0x{}'.format(hexstr)
    return hexstr


def remove_0x(hexstr):
    hexstr = normalize_hexstring(hexstr)
    return hexstr[2:]


def remove_0x_to_bytes(hexstr):
    return remove_0x(hexstr).encode('utf-8')


def to_bytes(s):
    return s.encode('utf-8')


def normalize_address(addr):
    return Web3.toChecksumAddress(normalize_hexstring(addr))


def hash_hexstring(hexbytes):
    assert hexbytes is not None, "hexbytes provided to hash_hexstring is None"
    return normalize_hexstring(Web3.sha3(hexstr=normalize_hexstring(hexbytes)))


def create_deploy_tx(w3inst, abi, bytecode, tx, *args, **kwargs):
    try:
        inst = w3inst.eth.contract(abi=abi, bytecode=bytecode)
        return inst.constructor(*args, **kwargs).buildTransaction(tx)
    except Exception as e:
        log.exception("Error creating deploy transaction")
        log.debug("create_deploy_tx args:\n{}\n{}".format(abi, bytecode))
        raise e
