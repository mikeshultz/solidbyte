""" Objects and utility functions for account operations """
import os
import json
from typing import TypeVar, List, Callable
from getpass import getpass
from pathlib import Path
from datetime import datetime
from attrdict import AttrDict
from eth_account import Account
from web3 import Web3
from ..common import to_path
from ..common import store
from ..common.exceptions import ValidationError
from ..common.logging import getLogger

log = getLogger(__name__)

T = TypeVar('T')


def autoload(f: Callable) -> Callable:
    """ Automatically load the metafile before method execution """
    def wrapper(*args, **kwargs):
        # A bit defensive, but make sure this is a decorator of a MetaFile method
        if len(args) > 0 and isinstance(args[0], Accounts):
            args[0]._load_accounts()
        return f(*args, **kwargs)
    return wrapper


class Accounts(object):
    def __init__(self, network_name: str = None,
                 keystore_dir: str = None,
                 web3: object = None) -> None:

        self.eth_account = Account()
        self.accounts = []

        if keystore_dir:
            self.keystore_dir = to_path(keystore_dir)
        else:
            # Try the session store first.
            if store.defined(store.Keys.KEYSTORE_DIR):
                self.keystore_dir = to_path(store.get(store.Keys.KEYSTORE_DIR))
            else:
                # Default to the standard loc
                self.keystore_dir = to_path('~/.ethereum/keystore')
        log.debug("Keystore directory: {}".format(self.keystore_dir))

        if web3:
            self.web3 = web3
        else:
            log.warning("Accounts initialized without a web3 instance.  Some things like gas price "
                        "estimation might be off or not working.")
            self.web3 = None

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
                    Web3.toChecksumAddress(json_object.get('address'))
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
                addr = Web3.toChecksumAddress(jason.get('address'))
                bal = -1
                if self.web3:
                    bal = self.web3.fromWei(
                        self.web3.eth.getBalance(self.web3.toChecksumAddress(addr)),
                        'ether'
                    )
                self.accounts.append(AttrDict({
                    'address': addr,
                    'filename': file,
                    'balance': bal,
                    'privkey': None
                }))

    def refresh(self) -> None:
        self._load_accounts(True)

    @autoload
    def _get_account_index(self, address: str) -> int:
        """ Return the list index for the account """
        idx = 0
        for a in self.accounts:
            if Web3.toChecksumAddress(a.address) == Web3.toChecksumAddress(address):
                return idx
            idx += 1
        raise IndexError("account does not exist")

    @autoload
    def get_account(self, address: str) -> AttrDict:
        """ Return all the known account addresses """

        for a in self.accounts:
            if Web3.toChecksumAddress(a.address) == Web3.toChecksumAddress(address):
                return a

        raise FileNotFoundError("Unable to find requested account")

    @autoload
    def account_known(self, address: str) -> bool:
        """ Check if an account is known """

        try:
            self._get_account_index(address)
            return True
        except IndexError:
            log.debug("Account {} is not locally managed in keystore {}".format(
                address,
                self.keystore_dir
            ))
            return False

    @autoload
    def get_accounts(self) -> List[AttrDict]:
        """ Return all the known account addresses """
        return self.accounts

    def set_account_attribute(self, address: str, key: str, val: T) -> None:
        """ Set an attribute of an account """
        idx = self._get_account_index(address)
        if idx < 0:
            raise IndexError("{} not found.  Unable to set attribute.".format(address))
        return setattr(self.accounts[idx], key, val)

    def create_account(self, password: str) -> str:
        """ Create a new account and encrypt it with password """

        new_account = self.eth_account.create(os.urandom(len(password) * 2))
        encrypted_account = Account.encrypt(new_account.privateKey, password)

        self._write_json_file(encrypted_account)

        return Web3.toChecksumAddress(new_account.address)

    @autoload
    def unlock(self, account_address: str, password: str = None) -> bytes:
        """ Unlock an account keystore file and return the private key """

        log.debug("Unlocking account {}".format(account_address))

        account = self.get_account(account_address)

        if account.privkey is not None:
            return account.privkey

        if not password:
            password = store.get(store.Keys.DECRYPT_PASSPHRASE)
            if not password:
                password = getpass("Enter password to decrypt account ({}):".format(
                    account_address
                ))
                if password:
                    store.set(store.Keys.DECRYPT_PASSPHRASE, password)

        jason = self._read_json_file(account.filename)
        privkey = self.eth_account.decrypt(jason, password)
        self.set_account_attribute(account_address, 'privkey', privkey)
        return privkey

    def sign_tx(self, account_address: str, tx: dict, password: str = None) -> str:
        """ Sign a transaction using the provided account """

        log.debug("Signing tx with account {}".format(account_address))

        if not self.web3:
            raise ValidationError("Unable to sign a transaction without an instantiated Web3 "
                                  "object.")

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
