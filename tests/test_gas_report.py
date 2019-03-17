""" Tests for the gas report module. """
from solidbyte.testing.gas import GasTransaction, GasReportStorage
from .const import TEST_HASH, ADDRESS_2_HASH, BYTECODE_HASH_1, ADDRESS_1, ADDRESS_2


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
    func_sigs = list(report.keys())
    assert len(func_sigs) == 1
    assert len(report[func_sigs[0]]) == 1
    assert expected_sig in func_sigs
    assert sum([sum(x) for x in report.values()]) == gas_used

    tx_hash2 = BYTECODE_HASH_1
    gas_used2 = gas_used + int(1e4)
    storage.add_transaction([{
        'from': ADDRESS_1,
        'to': ADDRESS_2,
        'value': 0,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'data': data,
    }])
    storage.update_last_transaction_set_hash(tx_hash2)
    storage.update_transaction_gas_used(tx_hash2, gas_used2)

    # Check the report
    report = storage.get_report(force=True)
    assert type(report) == dict
    func_sigs = list(report.keys())
    assert len(report[func_sigs[0]]) == 2
    assert expected_sig in func_sigs
    assert sum([sum(x) for x in report.values()]) == gas_used + gas_used2


def test_gas_report_storage_invalid_transactions():
    """ Test GasReportStorage with invalid transactions """

    storage = GasReportStorage()

    gas_limit = int(1e6)
    gas_price = int(3e9)
    data = TEST_HASH

    # No `gas` prop
    try:
        storage.add_transaction([{
            'from': ADDRESS_1,
            'to': ADDRESS_2,
            'value': 0,
            'gasPrice': gas_price,
            'data': data,
        }])
        assert False, "add_transaction() should have failed"
    except ValueError:
        pass

    # No `data` prop
    try:
        storage.add_transaction([{
            'from': ADDRESS_1,
            'to': ADDRESS_2,
            'value': 0,
            'gas': gas_limit,
            'gasPrice': gas_price,
        }])
        assert False, "add_transaction() should have failed"
    except ValueError:
        pass


def test_gas_report_storage_wrong_transactions():
    """ Test GasReportStorage by trying to update a tx that doesn't exist """

    storage = GasReportStorage()

    # This tx doesn't exist
    try:
        storage.update_transaction_gas_used(TEST_HASH, int(1e6))
        assert False, "update_transaction_gas_used() should have failed"
    except ValueError:
        pass
