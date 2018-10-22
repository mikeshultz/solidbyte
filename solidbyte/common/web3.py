# TODO: This should be alterable by the user
from web3.auto import w3 as web3
#from hexbytes import HexBytes

def deploy_contract(abi, bytecode):
    web3.eth.defaultAccount = web3.eth.accounts[0]
    inst = web3.eth.contract(abi=abi, bytecode=bytecode)
    deploy_txhash = inst.constructor().transact()
    deploy_receipt = web3.eth.waitForTransactionReceipt(deploy_txhash)
    return web3.eth.contract(abi=abi, address=deploy_receipt.contractAddress)

def normalize_address(addr):
    if isinstance(addr, bytes):
        addr = addr.hex()
    return addr

def normalize_hexstring(hexstr):
    if isinstance(hexstr, bytes):
        hexstr = hexstr.hex()
    return hexstr

def hash_hexstring(hexbytes):
    return normalize_hexstring(web3.sha3(hexstr=hexbytes))
