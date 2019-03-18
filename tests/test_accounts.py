from pathlib import Path
from solidbyte.accounts import Accounts
from solidbyte.common.web3 import web3c
from solidbyte.common.exceptions import SolidbyteException

from .const import (
    TMP_DIR,
    NETWORK_NAME,
    PASSWORD_1,
    NETWORKS_YML_1,
    ADDRESS_1,
    ADDRESS_2,
)
from .utils import write_temp_file, is_hex


def test_account_creation():
    # Mock up
    TMP_DIR.joinpath('keystore').mkdir(0o700, parents=True)
    write_temp_file(NETWORKS_YML_1, 'networks.yml', TMP_DIR, overwrite=True)

    web3c._load_configuration(TMP_DIR.joinpath('networks.yml'))
    web3 = web3c.get_web3(NETWORK_NAME)

    accounts = Accounts(
        network_name=NETWORK_NAME,
        web3=web3,
        keystore_dir=TMP_DIR.joinpath('keystore'),
    )
    assert len(accounts.accounts) == 0
    accts = accounts.get_accounts()
    assert len(accts) == 0

    new_acct_addr = accounts.create_account(PASSWORD_1)
    new_acct = accounts.get_account(new_acct_addr)
    keyfile = Path(new_acct.filename)
    assert keyfile.exists()

    privkey = accounts.unlock(new_acct_addr, PASSWORD_1)
    assert len(privkey) == 32

    # Fund the new account
    funding_txhash = web3.eth.sendTransaction({
            'from': web3.eth.accounts[0],
            'to': new_acct_addr,
            'value': int(2e18),
            'gas': 22000,
            'gasPrice': int(3e8)
        })
    funding_receipt = web3.eth.waitForTransactionReceipt(funding_txhash)
    assert funding_receipt.status == 1, "funding of test account failed"

    # Sign and send a tx
    value = int(1e18)  # 1 Ether
    raw_tx = accounts.sign_tx(new_acct_addr, {
            'from': new_acct_addr,
            'to': ADDRESS_1,
            'value': value,
            'gas': 22000,
            'gasPrice': int(3e8)
        }, PASSWORD_1)

    assert is_hex(raw_tx.rawTransaction)

    tx_hash = web3.eth.sendRawTransaction(raw_tx.rawTransaction)
    assert len(tx_hash) == 32
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    assert receipt.status == 1
    assert web3.eth.getBalance(ADDRESS_1) == value

    assert len(accounts.get_accounts()) == 1
    accounts.refresh()
    assert len(accounts.get_accounts()) == 1

    # Sign without gasPrice and send a tx
    # gas price strategy seems broken in web3.py
    # value = int(1e18)  # 1 Ether
    # raw_tx = accounts.sign_tx(new_acct_addr, {
    #         'from': new_acct_addr,
    #         'to': ADDRESS_1,
    #         'value': value,
    #         'gas': 22000,
    #     }, PASSWORD_1)
    # assert is_hex(raw_tx.rawTransaction)


def test_accounts_conflict_file(mock_project):
    with mock_project() as mock:

        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        # Put a file where the keystore dir should be
        keystore_path = mock.paths.project.joinpath('keystore')
        keystore_path.touch()

        try:
            Accounts(
                network_name=NETWORK_NAME,
                web3=web3,
                keystore_dir=keystore_path,
            )
            assert False, "Accounts.__init__() should fail on flie conflict"
        except SolidbyteException as err:
            assert 'Invalid keystore' in str(err)


def test_accounts_account_noexist(mock_project):
    with mock_project() as mock:

        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        # Put a file where the keystore dir should be
        keystore_path = mock.paths.project.joinpath('keystore')
        keystore_path.mkdir()

        accounts = Accounts(
            network_name=NETWORK_NAME,
            web3=web3,
            keystore_dir=keystore_path,
        )

        try:
            accounts.get_account(ADDRESS_2)
            assert False, "get_account() on invalid address should fail"
        except FileNotFoundError:
            pass

        try:
            accounts.set_account_attribute(ADDRESS_2, 'what', 'ever')
            assert False, "set_account_attribute() on invalid address should fail"
        except IndexError:
            pass
