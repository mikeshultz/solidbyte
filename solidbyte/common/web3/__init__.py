from web3 import Web3
from ...common.logging import getLogger
from .connection import Web3ConfiguredConnection

log = getLogger(__name__)
web3c = Web3ConfiguredConnection()

def create_deploy_tx(abi, bytecode, tx, *args, **kwargs):
    try:
        web3 = Web3()
        inst = web3.eth.contract(abi=abi, bytecode=bytecode)
        return inst.constructor(*args, **kwargs).buildTransaction(tx)
    except Exception as e:
        log.exception("Error creating deploy transaction")
        log.debug("create_deploy_tx args:\n{}\n{}".format(abi, bytecode))
        raise e

def normalize_hexstring(hexstr):
    if isinstance(hexstr, bytes):
        hexstr = hexstr.hex()
    if hexstr[:2] != '0x':
        hexstr = '0x{}'.format(hexstr)
    return hexstr

def normalize_address(addr):
    return Web3.toChecksumAddress(normalize_hexstring(addr))

def hash_hexstring(hexbytes):
    assert hexbytes is not None, "hexbytes provided to hash_hexstring is None"
    return normalize_hexstring(Web3.sha3(hexstr=normalize_hexstring(hexbytes)))
