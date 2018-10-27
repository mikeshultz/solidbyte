""" Objects and utility functions for account operations """
import os
import json
from pathlib import Path
from datetime import datetime
from attrdict import AttrDict
from eth_account import Account
from ..common.web3 import web3, normalize_hexstring
from ..common.logging import getLogger

log = getLogger(__name__)

class Accounts(object):
    def __init__(self, keystore_dir='~/.ethereum/keystore'):
        self.eth_account = Account()
        self.accounts = []
        self.keystore_dir=Path(keystore_dir).expanduser().resolve()

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
                    'balance': web3.fromWei(
                        web3.eth.getBalance(web3.toChecksumAddress(addr)),
                        'ether'
                        )
                }))

    def refresh():
        self._load_accounts(True)

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