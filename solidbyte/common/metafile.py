"""
Store and retrieve metdata about a contract for this project 

Example JSON structure:

    {
        "contracts": [
            {
                "name": "ExampleContract",
                "networks": {
                    "1": {
                        "deployedHash": "0xdeadbeef...",
                        "deployedInstances": [
                            {
                                "hash": "0xdeadbeef...",
                                "date": "2018-10-21 00:00:00T-7",
                                "address": "0xdeadbeef...",
                            }
                        ]
                    }
                }
            }
        ],
    }
"""
import json
from os import path
from datetime import datetime
from attrdict import AttrDict
from ..common import builddir
from ..common.logging import getLogger
from ..common.web3 import normalize_address, normalize_hexstring

log = getLogger(__name__)

METAFILE_FILENAME = 'metafile.json'

def autoload(f):
    """ Automatically load the metafile before method execution """
    def wrapper(*args, **kwargs):
        # A bit defensive, but make sure this is a decorator of a MetaFile method
        if len(args) > 0 and isinstance(args[0], MetaFile):
            args[0]._load()
        return f(*args, **kwargs)
    return wrapper

def autosave(f):
    """ Automatically save the metafile after method execution """
    def wrapper(*args, **kwargs):
        retval = f(*args, **kwargs)
        # A bit defensive, but make sure this is a decorator of a MetaFile method
        if len(args) > 0 and isinstance(args[0], MetaFile):
            args[0]._save()
    return wrapper

class MetaFile(object):
    """ Class representing the project metafile """

    def __init__(self):
        self.builddir = builddir()
        self.file_name = path.join(self.builddir, METAFILE_FILENAME)
        self._file = None
        self._json = None

    def _load(self):
        """ Lazily load the metafile """
        if not self._file:
            if not path.exists(self.file_name):
                with open(self.file_name, 'w') as openFile:
                    openFile.write('{}')
            with open(self.file_name, 'r') as openFile:
                self._file = openFile.read()
                self._json = json.loads(self._file)

    def _save(self):
        """ Save the metafile """
        with open(self.file_name, 'r+') as openFile:
            openFile.write(json.dumps(self._json, indent=2))
            self._file = openFile.read()
        return True

    @autoload
    def get_all_contracts(self):
        """ return all meta data for all contracts """

        if not self._json.get('contracts') or len(self._json['contracts']) < 1:
            return {}

        return self._json['contracts']

    @autoload
    def get_contract(self, name):
        """ Get the meta data for a contract """

        if not self._json.get('contracts') or len(self._json['contracts']) < 1:
            return None

        entries = list(filter(lambda x: x.get('name') == name, self._json['contracts']))
        if len(entries) > 1:
            raise Exception("Multiple entries for contract in metafile.json")
        elif len(entries) == 0:
            return None

        return entries[0]

    @autoload
    def get_contract_index(self, name):

        if not self._json.get('contracts') or len(self._json['contracts']) < 1:
            return None

        i = 0
        for ct in self._json['contracts']:
            if ct.get('name') == name:
                return i
            i += 1
        return None

    @autoload
    @autosave
    def add(self, name, network_id, address, abi, bytecode_hash):
        contract_idx = self.get_contract_index(name)
        address = normalize_address(address)
        bytecode_hash = normalize_hexstring(bytecode_hash)

        if contract_idx is not None:
            self._json['contracts'][contract_idx]['networks'][network_id]['deployedHash'] = bytecode_hash
            self._json['contracts'][contract_idx]['networks'][network_id]['deployedInstances'].append(AttrDict({
                'hash': bytecode_hash,
                'date': datetime.now().isoformat(),
                'address': address,
                'abi': abi,
                }))
        else:
            if not self._json.get('contracts'):
                self._json['contracts'] = []
            self._json['contracts'].append(AttrDict({
                'name': name,
                'networks': {
                    network_id: {
                        'deployedHash': bytecode_hash,
                        'deployedInstances': [
                            {
                                'hash': bytecode_hash,
                                'date': datetime.now().isoformat(),
                                'address': address,
                                'abi': abi,
                            }
                        ],
                    }
                }
                }))

    @autoload
    def account_known(self, address):
        """ Check if an account is known """
        if type(self._json['seenAccounts']) != list:
            return False

        account_idx = -1
        try:
            account_idx = self._json['seenAccounts'].index(address)
        except ValueError: pass

        if account_idx > -1:
            return True

        return False

    @autoload
    @autosave
    def add_account(self, address):
        """ Add an account to seenAccounts """
        address = normalize_address(address)

        if not self._json.get('seenAccounts'):
            self._json['seenAccounts'] = []

        if self.account_known(address):
            return

        self._json['seenAccounts'].append(address)

    @autoload
    @autosave
    def set_default_account(self, address):
        """ Set the default account """

        address = normalize_address(address)

        # Make sure we know about it
        self.add_account(address)

        self._json['defaultAccount'] = address

    @autoload
    def get_default_account(self):
        """ Get the default account """
        return self._json.get('defaultAccount')
