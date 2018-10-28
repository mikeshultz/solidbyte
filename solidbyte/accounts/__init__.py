""" Objects and utility functions for account operations """
import os
import json
from getpass import getpass
from pathlib import Path
from datetime import datetime
from attrdict import AttrDict
from eth_account import Account
from ..common.web3 import web3c, normalize_hexstring
from ..common.logging import getLogger

log = getLogger(__name__)

class Accounts(object):
    def __init__(self, network_name=None, keystore_dir='~/.ethereum/keystore'):
        self.eth_account = Account()
        self.accounts = []
        self.keystore_dir=Path(keystore_dir).expanduser().resolve()
        self.web3 = web3c.get_web3(network_name)

        if not self.keystore_dir.is_dir():
            log.error("Provided keystore directory is not a directory")
            raise Exception("Invalid keystore directory")

    def _read_json_file(self, filename):
        """ Read a JSON file and output a python dict """
        jason = None
        with open(filename, 'r') as json_file:
            try:
                file_string = json_file.read()
                jason = json.loads(file_string)
            except Exception as e:
                log.error("Error reading JSON file {}: {}".format(filename, str(e)))
        return jason

    def _write_json_file(self, json_object, filename=None):
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

    def _get_keystore_files(self):
        """ Return all filenames of keystore files """
        return self.keystore_dir.iterdir()

    def _load_accounts(self, force=False):
        if len(self.accounts) > 1 and not force:
            return

        self.accounts = []
        for file in self._get_keystore_files():
            jason = self._read_json_file(file)
            if not jason:
                log.warning("Unable to read JSON from {}".format(file))
            else:
                addr = normalize_hexstring(jason.get('address'))
                self.accounts.append(AttrDict({
                    'address': addr,
                    'filename': file,
                    'balance': self.web3.fromWei(
                        self.web3.eth.getBalance(self.web3.toChecksumAddress(addr)),
                        'ether'
                        )
                }))

    def refresh():
        self._load_accounts(True)

    def get_account(self, address):
        """ Return all the known account addresses """

        self._load_accounts()

        for a in self.accounts:
            if a.address == address:
                return a

        raise FileNotFoundError("Unable to find requested account")

    def get_accounts(self):
        """ Return all the known account addresses """

        self._load_accounts()

        return self.accounts

    def create_account(self, password):
        """ Create a new account and encrypt it with password """

        new_account = self.eth_account.create(os.urandom(len(password) * 2))
        encrypted_account = Account.encrypt(new_account.privateKey, password)

        self._write_json_file(encrypted_account)

        return new_account.address

    def unlock(self, account_address, password=None):
        """ Unlock an account keystore file and return the private key """

        log.debug("Unlocking account {}".format(account_address))

        if not password:
            password = getpass("Enter password to decrypt account ({}):".format(account_address))

        account = self.get_account(account_address)
        jason = self._read_json_file(account.filename)
        return self.eth_account.decrypt(jason, password)

    def sign_tx(self, account_address, tx, password=None):
        """ Sign a transaction using the provided account """

        log.debug("Signing tx with account {}".format(account_address))

        if not password:
            password = getpass("Enter password to decrypt account ({}):".format(account_address))

        privkey = self.unlock(account_address, password)
        return self.web3.eth.account.signTransaction(tx, privkey)
