import sys
# TODO: This should be alterable by the user
from web3.auto import w3 as web3
from ..common.logging import getLogger

log = getLogger(__name__)

def deploy_contract(abi, bytecode, *args, **kwargs):
    try:
        web3.eth.defaultAccount = web3.eth.accounts[0]
        inst = web3.eth.contract(abi=abi, bytecode=bytecode)
        deploy_txhash = inst.constructor(*args, **kwargs).transact()
        deploy_receipt = web3.eth.waitForTransactionReceipt(deploy_txhash)
        return deploy_receipt.contractAddress
    except Exception as e:
        log.exception("Error deploying contract")
        log.debug("deploy_contract args:\n{}\n{}".format(abi, bytecode))
        raise e

def normalize_hexstring(hexstr):
    if isinstance(hexstr, bytes):
        hexstr = hexstr.hex()
    if hexstr[:2] != '0x':
        hexstr = '0x{}'.format(hexstr)
    return hexstr

def normalize_address(addr):
    return normalize_hexstring(addr)

def hash_hexstring(hexbytes):
    assert hexbytes is not None, "hexbytes provided to hash_hexstring is None"
    return normalize_hexstring(web3.sha3(hexstr=normalize_hexstring(hexbytes)))
