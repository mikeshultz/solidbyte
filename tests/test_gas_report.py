""" Tests for the gas report module. """
from solidbyte.testing.gas import GasTransaction, GasReportStorage
from .const import TEST_HASH, ADDRESS_2_HASH, ADDRESS_1, ADDRESS_2


def test_transaction(mock_project):
    """ test the GasTransaction object is as expected """

    gas_limit = int(1e6)
    gt = GasTransaction(gas_limit, TEST_HASH)

    expected_sig = TEST_HASH[2:10]

    assert gt.gas_limit == gas_limit
    assert gt.data == TEST_HASH
    assert gt.func_sig == expected_sig

    assert gt.gas_used is None
    assert gt.tx_hash is None


def test_gas_report_storage():
    """ Test GasReportStorage """

    storage = GasReportStorage()

    assert storage.total_gas == 0
    assert type(storage.report) == dict
    assert len(storage.report) == 0
    assert type(storage.transactions) == list
    assert len(storage.transactions) == 0

    # Add one tx
    gas_limit = int(1e6)
    gas_price = int(3e9)
    gas_used = int(75000)
    tx_hash = ADDRESS_2_HASH
    data = TEST_HASH
    expected_sig = data[2:10]
    storage.add_transaction([{
        'from': ADDRESS_1,
        'to': ADDRESS_2,
        'value': 0,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'data': data,
    }])

    assert len(storage.transactions) == 1

    last_tx = storage.transactions[0]
    assert last_tx.gas_limit == gas_limit
    assert last_tx.data == TEST_HASH
    assert last_tx.tx_hash is None
    assert last_tx.gas_used is None

    # Update the tx hash
    storage.update_last_transaction_set_hash(tx_hash)

    assert last_tx.tx_hash == tx_hash

    # Update the gas used manually
    storage.update_transaction_gas_used(tx_hash, gas_used)

    assert last_tx.gas_used == gas_used

    # Check the report
    report = storage.get_report()
    assert type(report) == dict
    func_sigs = report.keys()
    assert len(func_sigs) == 1
    assert expected_sig in func_sigs
    print("values: ", report.values())
    assert sum([sum(x) for x in report.values()]) == gas_used
