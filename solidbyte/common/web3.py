import sys
# TODO: This should be alterable by the user
from web3.auto import w3 as web3
from ..common.logging import getLogger

log = getLogger(__name__)

def create_deploy_tx(abi, bytecode, tx, *args, **kwargs):
    try:
        inst = web3.eth.contract(abi=abi, bytecode=bytecode)
        return inst.constructor(*args, **kwargs).buildTransaction(tx)
    except Exception as e:
        log.exception("Error creating deploy transaction")
        log.debug("create_deploy_tx args:\n{}\n{}".format(abi, bytecode))
        raise e

def next_nonce(address):
    return web3.eth.getTransactionCount(address)

def normalize_hexstring(hexstr):
    if isinstance(hexstr, bytes):
        hexstr = hexstr.hex()
    if hexstr[:2] != '0x':
        hexstr = '0x{}'.format(hexstr)
    return hexstr

def normalize_address(addr):
    return web3.toChecksumAddress(normalize_hexstring(addr))

def hash_hexstring(hexbytes):
    assert hexbytes is not None, "hexbytes provided to hash_hexstring is None"
    return normalize_hexstring(web3.sha3(hexstr=normalize_hexstring(hexbytes)))
