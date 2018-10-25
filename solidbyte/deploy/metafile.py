""" Store and retrieve metdata about a contract for this project """
import json
from os import path
from datetime import datetime
from ..common import builddir
from ..common.logging import getLogger
from ..common.web3 import normalize_address, normalize_hexstring

log = getLogger(__name__)

METAFILE_FILENAME = 'metafile.json'

class MetaFile(object):
    """ Class representing the project metafile """

    def __init__(self):
        self.builddir = builddir()
        self.file_name = path.join(self.builddir, METAFILE_FILENAME)
        self._file = None
        self._json = None

    def _lazy_load(self):
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

    def get_all_contracts(self):
        """ return all meta data for all contracts """

        self._lazy_load()

        if not self._json.get('contracts') or len(self._json['contracts']) < 1:
            return None

        return self._json['contracts']

    def get_contract(self, name):
        """ Get the meta data for a contract """

        self._lazy_load()

        if not self._json.get('contracts') or len(self._json['contracts']) < 1:
            return None

        entries = list(filter(lambda x: x.get('name') == name, self._json['contracts']))
        if len(entries) > 1:
            raise Exception("Multiple entries for contract in metafile.json")
        elif len(entries) == 0:
            return None

        return entries[0]

    def get_contract_index(self, name):

        self._lazy_load()

        if not self._json.get('contracts') or len(self._json['contracts']) < 1:
            return None

        i = 0
        for ct in self._json['contracts']:
            if ct.get('name') == name:
                return i
            i += 1
        return None

    def add(self, name, address, bytecode_hash):
        contract_idx = self.get_contract_index(name)
        address = normalize_address(address)
        bytecode_hash = normalize_hexstring(bytecode_hash)

        if contract_idx is not None:
            self._json['contracts'][contract_idx]['deployedHash'] = bytecode_hash
            self._json['contracts'][contract_idx]['deployedInstances'].append({
                'hash': bytecode_hash,
                'date': datetime.now().isoformat(),
                'address': address,
                })
        else:
            if not self._json.get('contracts'):
                self._json['contracts'] = []
            self._json['contracts'].append({
                'name': name,
                'deployedHash': bytecode_hash,
                'deployedInstances': [
                    {
                        'hash': bytecode_hash,
                        'date': datetime.now().isoformat(),
                        'address': address,
                    }
                ],
                })

        return self._save()
