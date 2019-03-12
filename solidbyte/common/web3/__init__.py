from web3 import Web3
from hexbytes import HexBytes
from ..logging import getLogger
from ..exceptions import DeploymentValidationError
from .connection import Web3ConfiguredConnection

log = getLogger(__name__)
web3c = Web3ConfiguredConnection()


NO_FUNCTION_CALL_INPUTS = ['']


def normalize_hexstring(hexstr):
    if isinstance(hexstr, HexBytes):
        hexstr = hexstr.hex()
    elif isinstance(hexstr, bytes):
        hexstr = hexstr.decode('utf-8')
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


def hash_string(strong):
    assert strong is not None, "strong provided to hash_string is None"
    return normalize_hexstring(Web3.sha3(text=strong))


def clean_bytecode(bytecode):
    """ Cleanup bytecode for web3.py """
    # Remove comment lines
    bytecode = '\n'.join([ln.strip() for ln in bytecode.split('\n') if not ln.startswith('//')])
    # remove spurious newlines
    bytecode = bytecode.strip('\n')
    # Normalize and strip 0x because web3.py doesn't like it
    return remove_0x(normalize_hexstring(bytecode))


def abi_has_constructor(abi) -> bool:
    """ See if the ABI has a definition for a constructor """
    if not abi or len(abi) < 1:
        return False
    for _def in abi:
        if _def.get('type') == 'constructor':
            return True
    return False


def func_sig_from_input(data):
    """ Return the 4-byte function signature from a transaction input field """
    if data in NO_FUNCTION_CALL_INPUTS:
        return None
    return remove_0x(data)[:8]


def create_deploy_tx(w3inst, abi, bytecode, tx, *args, **kwargs):
    # Verify
    try:
        assert w3inst is not None, "Invalid web3 instance"
        assert abi is not None, "Invalid contract ABI"
        assert bytecode is not None and bytecode != '0x', "Missing bytecode!"
    except AssertionError:
        log.error("Invalid input to create_deploy_tx.")
        log.debug("create_deploy_tx(web3inst={}, abi={}, bytecode={}, tx={}".format(
                w3inst,
                abi,
                bytecode,
                tx
            ))
        raise DeploymentValidationError("Deployment parameter validation failed.")
    try:
        inst = w3inst.eth.contract(abi=abi, bytecode=clean_bytecode(bytecode))
        if abi_has_constructor(abi):
            deploy_tx = inst.constructor(*args, **kwargs).buildTransaction(tx)
        else:
            # web3.py still uses constructor() even if the contract does not have a constructor
            deploy_tx = inst.constructor().buildTransaction(tx)
        return deploy_tx
    except Exception as e:
        log.exception("Error creating deploy transaction")
        log.debug("create_deploy_tx args:\n{}\n{}\n{}".format(abi, bytecode, tx))
        raise e
