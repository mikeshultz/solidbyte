""" Utility functions to be provided as pytest fixtures for Solidbyte testing """
import math
from typing import Union, Optional
from datetime import datetime
from hexbytes import HexBytes
from attrdict import AttrDict
from web3 import Web3
from web3.datastructures import AttributeDict
from web3.contract import Contract as Web3Contract
from web3.utils.events import get_event_data

MultiDict = Union[dict, AttrDict, AttributeDict]


def topic_signature(abi: MultiDict) -> HexBytes:
    if abi.get('type') != 'event':
        return None
    args = ''
    if abi.get('inputs'):
        args = ','.join([a.get('type') for a in abi['inputs']])
    sig = '{}({})'.format(abi.get('name'), args)
    return Web3.sha3(text=sig)


def event_abi(contract_abi: MultiDict, name: str) -> Optional[AttributeDict]:
    for abi in contract_abi:
        if abi.get('type') == 'event' and abi.get('name') == name:
            return abi
    return None


def get_event(web3contract: Web3Contract, event_name: str,
              rcpt: MultiDict) -> Optional[AttributeDict]:
    """ Return the event data from a transaction receipt

    :param web3contract: (:class:`web3.contract.Contract`) The contract that has the event ABI we
        are looking for.
    :param event_name: (:code:`str`) the name of the event
    :param rcpt: (:code:`dict`) object of the transaction receipt
    :returns: (:code:`dict`) the event data
    """
    if rcpt.get('logs') and len(rcpt['logs']) < 1:
        return None

    abi = event_abi(web3contract.abi, event_name)

    for log in rcpt['logs']:
        evnt_data = get_event_data(abi, log)
        return evnt_data
    return None


def has_event(web3contract: Web3Contract, event_name: str, rcpt: MultiDict) -> bool:
    """ Check if a receipt contains an event by name

    :param web3contract: (:class:`web3.contract.Contract`) The contract that has the event ABI we
        are looking for.
    :param event_name: (:code:`str`) the name of the event
    :param rcpt: (:code:`dict`) object of the transaction receipt
    :returns: (:code:`bool`)
    """
    abi = event_abi(web3contract.abi, event_name)
    if abi is None:
        raise ValueError("Did not find {} in contract ABI.".format(event_name))
    sig = HexBytes(topic_signature(abi).hex())
    for log in rcpt['logs']:
        if len(log['topics']) > 0 and log['topics'][0] == sig:
            return True
    return False


def time_travel(web3: Web3, secs: int) -> int:
    """ Time travel the chain

    :param web3: (:class:`web3.Web3`) object to use for connection
    :param secs: (:code:`int`) of the amount of seconds to travel forward in time
    :returns: (:code:`int`) the latest block number
    """
    block_before = web3.eth.getBlock('latest')
    now = int(datetime.now().timestamp())
    drift = 30  # A magical amount of correction for drift that eth_tester sometimes has

    # eth_tester
    try:
        web3.testing.timeTravel(now + secs + drift)
        web3.testing.mine(1)  # Get one block in, at least
    except ValueError as err:
        if 'not supported' in str(err):
            # Ganache/testrpc
            assert len(web3.providers) > 0, "No web3 providers found"
            web3.providers[0].make_request('evm_increaseTime', [secs])

            # for evm_mine, ganache takes a timestmap for some reason, and it isn't reflected in the
            # logs, either, so there's that.
            web3.testing.mine(int(block_before.timestamp) + secs)
        else:
            raise err

    # Verify
    block_after = web3.eth.getBlock('latest')
    assert block_before.number < block_after.number, "Time travel failed"
    stamp_diff = int(block_after.timestamp) - int(block_before.timestamp)

    assert stamp_diff >= secs, (
        "Not enough time passed.  Only {} seconds.  Wanted {} seconds.".format(stamp_diff, secs)
    )
    return block_after.number


def block_travel(web3: Web3, blocks: int) -> int:
    """ Travel forward X blocks

    :param web3: (:class:`web3.Web3`) object to use for connection
    :param secs: (:code:`int`) of the amount of blocks to travel forward in time
    :returns: (:code:`int`) the latest block number
    """
    block_before = web3.eth.getBlock('latest')
    web3.testing.mine(math.ceil(blocks))
    block_after = web3.eth.getBlock('latest')
    assert block_after.number - block_before.number == blocks, "Block travel failed"
    return block_after.number
