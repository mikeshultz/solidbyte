""" Tests functions that are used as pytest fixtures for Solidbyte testing """
from web3 import Web3
from solidbyte.common.web3 import web3c
from solidbyte.testing.fixtures import (
    topic_signature,
    event_abi,
    has_event,
    get_event,
    std_tx,
    time_travel,
    block_travel,
)
from .const import (
    ADDRESS_1,
    ADDRESS_2,
    NETWORKS_YML_1,
    DUMB_CONTRACT_ABI,
    EVENT_ABI,
    EVENT_SIG_HASH,
    EVENT_RECEIPT,
)


class ContractMock(object):
    """ These functions only look for the abi attribute """
    abi = DUMB_CONTRACT_ABI


def test_topic_signature():
    assert topic_signature(EVENT_ABI) == EVENT_SIG_HASH


def test_event_abi():
    assert event_abi(DUMB_CONTRACT_ABI, 'AddressEvent') == EVENT_ABI


def test_has_event():
    web3 = Web3()
    contract = web3.eth.contract(abi=DUMB_CONTRACT_ABI)
    assert has_event(contract, 'AddressEvent', EVENT_RECEIPT)


def test_get_event():
    web3 = Web3()
    contract = web3.eth.contract(abi=DUMB_CONTRACT_ABI)
    evnt = get_event(contract, 'AddressEvent', EVENT_RECEIPT)
    assert evnt.event == 'AddressEvent'
    assert evnt.args.val == '0x717dD920E935b5078fC67717713b2A62987A8044'


def test_std_tx():
    value = int(1e18)  # 1ether

    # update a tx without gas or gasPrice
    tx = std_tx({
        'from': ADDRESS_1,
        'to': ADDRESS_2,
        'value': value,
    })
    assert 'gas' in tx
    assert 'gasPrice' in tx
    assert tx.get('from') == ADDRESS_1
    assert tx.get('to') == ADDRESS_2
    assert tx.get('value') == value

    # update a tx with gas and gasPrice
    gas = int(2100)
    gas_price = int(2e9)  # 2gwei

    tx = std_tx({
        'to': ADDRESS_1,
        'from': ADDRESS_2,
        'value': value,
        'gas': gas,
        'gasPrice': gas_price,
    })
    assert 'gas' in tx
    assert 'gasPrice' in tx
    assert tx.get('to') == ADDRESS_1
    assert tx.get('from') == ADDRESS_2
    assert tx.get('value') == value
    assert tx.get('gas') == gas
    assert tx.get('gasPrice') == gas_price


def test_time_travel(ganache, temp_dir):

    with ganache() as gopts:
        with temp_dir() as workdir:

            networksyml = workdir.joinpath('networks.yml')

            with networksyml.open('w') as _file:
                _file.write(NETWORKS_YML_1)

            web3c._load_configuration(networksyml)
            web3 = web3c.get_web3(gopts.network_name)

            start_block = web3.eth.getBlock('latest')

            five_minutes = 5*60
            latest_block_number = time_travel(web3, five_minutes)
            latest_block = web3.eth.getBlock(latest_block_number)

            timediff = latest_block.timestamp - start_block.timestamp
            assert timediff > 0
            assert timediff >= five_minutes, (
                "time travel failed.  Expected {} received {}".format(five_minutes, timediff)
            )


def test_block_travel(ganache, temp_dir):

    with ganache() as gopts:
        with temp_dir() as workdir:

            networksyml = workdir.joinpath('networks.yml')

            with networksyml.open('w') as _file:
                _file.write(NETWORKS_YML_1)

            web3c._load_configuration(networksyml)
            web3 = web3c.get_web3(gopts.network_name)

            start_block = web3.eth.getBlock('latest')

            blocks_to_travel = 5
            latest_block_number = block_travel(web3, blocks_to_travel)
            latest_block = web3.eth.getBlock(latest_block_number)

            expected_block = start_block.number + blocks_to_travel
            assert latest_block.timestamp > start_block.timestamp
            assert latest_block.number == expected_block, (
                "block travel failed.  Expected {} blocks, but only saw {} blocks".format(
                    expected_block,
                    latest_block.number,
                )
            )
