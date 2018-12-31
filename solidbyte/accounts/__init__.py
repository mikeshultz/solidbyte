""" Objects and utility functions for account operations """
import os
import json
from typing import TypeVar, List
from getpass import getpass
from pathlib import Path
from datetime import datetime
from attrdict import AttrDict
from eth_account import Account
from web3 import Web3
from ..common.logging import getLogger

log = getLogger(__name__)

T = TypeVar('T')


class Accounts(object):
    def __init__(self, network_name: str = None,
                 keystore_dir: str = '~/.ethereum/keystore',
                 web3: object = None) -> None:
        self.eth_account = Account()
        self.accounts = []
        self.keystore_dir = Path(keystore_dir).expanduser().resolve()
        if web3:
            self.web3 = web3
        else:
            self.web3 = Web3()

        if not self.keystore_dir.is_dir():
            if self.keystore_dir.exists():
                log.error("Provided keystore directory is not a directory")
                raise Exception("Invalid keystore directory")
            else:
                self.keystore_dir.mkdir(mode=0o700, parents=True)

    def _read_json_file(self, filename: str) -> object:
        """ Read a JSON file and output a python dict """
        jason = None
        with open(filename, 'r') as json_file:
            try:
                file_string = json_file.read()
                jason = json.loads(file_string)
            except Exception as e:
                log.error("Error reading JSON file {}: {}".format(filename, str(e)))
        return jason

    def _write_json_file(self, json_object: object, filename: str = None) -> None:
        """ Write a JSON file from a python dict """

        if type(filename) == str:
            filename = Path(filename).expanduser().resolve()
        if not filename:
            filename = self.keystore_dir.joinpath(
                'UTC--{}--{}'.format(
                    datetime.now().isoformat(),
                    json_object.get('address')
                    )
                )
        with open(filename, 'w') as json_file:
            try:
                jason = json.dumps(json_object)
                json_file.write(jason)
            except Exception as e:
                log.error("Error writing JSON file {}: {}".format(filename, str(e)))

    def _get_keystore_files(self) -> list:
        """ Return all filenames of keystore files """
        return self.keystore_dir.iterdir()

    def _load_accounts(self, force: bool = False) -> None:
        if len(self.accounts) > 1 and not force:
            return

        self.accounts = []
        for file in self._get_keystore_files():
            jason = self._read_json_file(file)
            if not jason:
                log.warning("Unable to read JSON from {}".format(file))
            else:
                addr = self.web3.toChecksumAddress(jason.get('address'))
                self.accounts.append(AttrDict({
                    'address': addr,
                    'filename': file,
                    'balance': self.web3.fromWei(
                        self.web3.eth.getBalance(self.web3.toChecksumAddress(addr)),
                        'ether'
                        ),
                    'privkey': None
                }))

    def refresh(self) -> None:
        self._load_accounts(True)

    def _get_account_index(self, address: str) -> int:
        """ Return the list index for the account """
        idx = 0
        for a in self.accounts:
            if a.address == address:
                return idx
            idx += 1
        raise IndexError("account does not exist")

    def get_account(self, address: str) -> AttrDict:
        """ Return all the known account addresses """

        self._load_accounts()

        for a in self.accounts:
            if a.address == address:
                return a

        raise FileNotFoundError("Unable to find requested account")

    def account_known(self, address: str) -> bool:
        """ Check if an account is known """
        try:
            self._get_account_index(address)
            return True
        except IndexError:
            return False

    def get_accounts(self) -> List[AttrDict]:
        """ Return all the known account addresses """

        self._load_accounts()

        return self.accounts

    def set_account_attribute(self, address: str, key: str, val: T) -> None:
        """ Set an attribute of an account """
        idx = 0
        for a in self.accounts:
            if a.address == address:
                setattr(self.accounts[idx], key, val)
                return
            idx += 1

    def create_account(self, password: str) -> str:
        """ Create a new account and encrypt it with password """

        new_account = self.eth_account.create(os.urandom(len(password) * 2))
        encrypted_account = Account.encrypt(new_account.privateKey, password)

        self._write_json_file(encrypted_account)

        return new_account.address

    def unlock(self, account_address: str, password: str = None) -> bytes:
        """ Unlock an account keystore file and return the private key """

        log.debug("Unlocking account {}".format(account_address))

        account = self.get_account(account_address)

        if account.privkey is not None:
            return account.privkey

        if not password:
            password = getpass("Enter password to decrypt account ({}):".format(account_address))

        jason = self._read_json_file(account.filename)
        privkey = self.eth_account.decrypt(jason, password)
        self.set_account_attribute(account_address, 'privkey', privkey)
        return privkey

    def sign_tx(self, account_address: str, tx: dict, password: str = None) -> str:
        """ Sign a transaction using the provided account """

        log.debug("Signing tx with account {}".format(account_address))

        """ Do some tx verification and substitution if necessary
        """
        if tx.get('gasPrice') is None:
            gasPrice = self.web3.eth.generateGasPrice()
            log.warning("Missing gasPrice for transaction. Using automatic price of {}".format(
                    gasPrice
                ))
            tx['gasPrice'] = gasPrice

        if tx.get('nonce') is None:
            nonce = self.web3.eth.getTransactionCount(tx['from'])
            tx['nonce'] = nonce

        privkey = self.unlock(account_address, password)
        return self.web3.eth.account.signTransaction(tx, privkey)
