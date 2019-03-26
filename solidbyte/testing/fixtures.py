""" Utility functions to be provided as pytest fixtures for Solidbyte testing """
import math
import time
from typing import Union, Optional
from datetime import datetime
from hexbytes import HexBytes
from attrdict import AttrDict
from web3 import Web3
from web3.datastructures import AttributeDict
from web3.contract import Contract as Web3Contract
from web3.utils.events import get_event_data
from ..common import MAX_PRODUCTION_NETWORK_ID
from ..common.exceptions import SolidbyteException
from ..common.logging import getLogger

log = getLogger(__name__)

MultiDict = Union[dict, AttrDict, AttributeDict]

STD_GAS = int(1e6)
STD_GAS_PRICE = int(3e9)  # 3gwei


def std_tx(tx: MultiDict):
    """ Create a test transaction with default gas and gasPrice

    :param tx: (:code:`dict`) representation of an Ethereum transaction
    :returns: (:code:`dict`) representation of an Ethereum transaction with defaults
    """
    std = {
        'gas': STD_GAS,
        'gasPrice': STD_GAS_PRICE,
    }
    std.update(tx)
    return std


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


def block_travel(web3: Web3, blocks: int, block_time: int = 1) -> int:
    """ Travel forward X blocks

    :param web3: (:class:`web3.Web3`) object to use for connection
    :param secs: (:code:`int`) of the amount of blocks to travel forward in time
    :param block_time: (:code:`int`) the expected block time of the chain, in seconds. (default: 1)
    :returns: (:code:`int`) the latest block number
    """

    log.warning("block_travel is experimental and should only be used on test networks!")

    block_before = web3.eth.getBlock('latest')
    block_travel = math.ceil(blocks)

    """ Every damned implementation of this functionality is a little different.  There's some
    assumptions being made here.

        - If it's eth_tester, use :code:`web3.testing.mine`
        - If not, start the miner if necessary
        - Look and see if blocks are being mined within the given block_time (custom test
          go-ethereum instances with miner scripts, for instance)
        - If new blocks are not being mined in that window, send some empty transactions to trigger
          the miner(ganache)
    """

    if hasattr(web3, 'is_eth_tester') and web3.is_eth_tester:

        web3.testing.mine(block_travel)

    else:

        net_id = int(web3.version.network)
        assert net_id > MAX_PRODUCTION_NETWORK_ID, (
            "Can not block travel on network {}".format(net_id)
        )

        started_miner = False
        if web3.miner.hashrate == 0:
            web3.miner.start(1)
            started_miner = True

        new_block = None
        sleep_time = 0.5
        max_wait = math.ceil((block_time / sleep_time) + 1)
        loop_count = 0
        send_empty_transactions = False
        while new_block is None or (new_block.number < block_before.number + block_travel):
            new_block = web3.eth.getBlock('latest')
            log.debug("Waiting for block #{}. Seen block #{}".format(
                block_before.number + block_travel,
                new_block.number,
            ))
            loop_count += 1
            if loop_count > max_wait and (new_block and new_block.number == block_before.number):
                send_empty_transactions = True
                break
            time.sleep(0.5)

        # Some test backends, like ganache, won't mine until they have a tx
        if send_empty_transactions:

            from_account = web3.eth.accounts[0]
            to_account = web3.eth.accounts[1]
            while new_block is None or (new_block.number < block_before.number + block_travel):

                tx_hash = web3.eth.sendTransaction({
                    'from': from_account,
                    'to': to_account,
                    'value': 0,
                    'data': '0x1',
                    'gasPrice': int(3e9),
                })

                log.debug("Sent transaction {} to trigger miner. Waiting for miner...".format(
                    tx_hash
                ))

                receipt = web3.eth.waitForTransactionReceipt(tx_hash)

                if receipt.status != 1:
                    raise SolidbyteException("Unable to block travel on network_id {}".format(
                        net_id
                    ))

                log.debug("Transaction {} has been mined.".format(tx_hash))

                new_block = web3.eth.getBlock('latest')

                log.debug("Waiting for block #{}. Seen block #{}".format(
                    block_before.number + block_travel,
                    new_block.number,
                ))

        if started_miner:
            web3.miner.stop()

        block_after = new_block

    assert block_after.number - block_before.number == blocks, (
        "Block travel failed. Expected block #{}, received #{}".format(
            block_before.number + blocks,
            block_after.number,
        )
    )

    return block_after.number
