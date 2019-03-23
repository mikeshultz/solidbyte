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
        "seenAccounts": [
            "0xdeadbeef..."
        ],
        "defaultAccount": "0xdeadbeef..."
    }
"""
import json
from typing import Union, Any, Optional, Callable, List, Tuple
from pathlib import Path
from datetime import datetime
from functools import wraps
from shutil import copyfile
from attrdict import AttrDict
from .logging import getLogger
from .utils import hash_file, to_path_or_cwd
from .web3 import normalize_address, normalize_hexstring

log = getLogger(__name__)

METAFILE_FILENAME = 'metafile.json'
NETWORK_ID_MAX_OFFICIAL = 100

T = Union[Any, None]
PS = Union[Path, str]


def autoload(f: Callable) -> Callable:
    """ Automatically load the metafile before method execution """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # A bit defensive, but make sure this is a decorator of a MetaFile method
        if len(args) > 0 and isinstance(args[0], MetaFile):
            args[0]._load()
        return f(*args, **kwargs)
    return wrapper


def autosave(f):
    """ Automatically save the metafile after method execution """
    @wraps(f)
    def wrapper(*args, **kwargs):
        retval = f(*args, **kwargs)
        # A bit defensive, but make sure this is a decorator of a MetaFile method
        if len(args) > 0 and isinstance(args[0], MetaFile):
            args[0]._save()
        return retval
    return wrapper


class MetaFile:
    """ Class representing the project metafile """

    def __init__(self,
                 filename_override: PS = None,
                 project_dir: PS = None,
                 read_only: bool = False) -> None:

        self._file: Optional[str] = None
        self._json: Optional[dict] = None
        self.project_dir = to_path_or_cwd(project_dir)
        self.file_name = self.project_dir.joinpath(filename_override or METAFILE_FILENAME)
        self._read_only = read_only

    def _load(self) -> None:
        """ Lazily load the metafile """

        if self._read_only:
            log.warning("metafile.json opened read-only.  Not loading from disk!")
            # Create _json if necessary
            if self._json is None:
                self._file = '{}'
                self._json = json.loads(self._file)
                return

        if not self._read_only:

            if not self._file:

                if not self.file_name.exists():

                    with open(self.file_name, 'x') as openFile:
                        openFile.write('{}')

                    log.info("New metafile.json created.")

                with open(self.file_name, 'r') as openFile:
                    self._file = openFile.read()
                    log.debug("Reloaded metafile.json from file.")
                    self._json = json.loads(self._file)

    def _save(self):
        """ Save the metafile """
        self._file = json.dumps(self._json, indent=2)
        if self._read_only:
            log.warning("metafile.json opened read only.  Not saving to disk!")
            return False

        with open(self.file_name, 'w') as openFile:
            openFile.write(self._file)
        self._load()
        return True

    @autoload
    def get_all_contracts(self) -> List[AttrDict]:
        """ return all meta data for all contracts """

        if self._json is None or not self._json.get('contracts') \
                or len(self._json['contracts']) < 1:
            return []

        return self._json['contracts']

    @autoload
    def get_contract(self, name) -> AttrDict:
        """ Get the meta data for a contract """

        if self._json is None or not self._json.get('contracts') \
                or len(self._json['contracts']) < 1:
            return None

        entries = list(filter(lambda x: x.get('name') == name, self._json['contracts']))
        if len(entries) > 1:
            raise Exception("Multiple entries for contract in metafile.json")
        elif len(entries) == 0:
            return None

        return entries[0]

    @autoload
    def get_contract_index(self, name: str) -> int:

        if self._json is None or not self._json.get('contracts') \
                or len(self._json['contracts']) < 1:
            return -1

        i = 0
        for ct in self._json['contracts']:
            if ct.get('name') == name:
                return i
            i += 1
        return -1

    @autoload
    @autosave
    def add(self, name: str, _network_id: int, address: str, abi: dict,
            bytecode_hash: str) -> None:

        if self._json is None:
            raise Exception("Invalid configuration. Corrupted file?")

        contract_idx = self.get_contract_index(name)
        address = normalize_address(address)
        bytecode_hash = normalize_hexstring(bytecode_hash)
        network_id = str(_network_id)

        if contract_idx > -1:
            if not self._json['contracts'][contract_idx]['networks'].get(network_id):
                self._json['contracts'][contract_idx]['networks'][network_id] = AttrDict({
                    'deployedHash': '',
                    'deployedInstances': []
                    })

            (self._json['contracts']
                       [contract_idx]
                       ['networks']
                       [network_id]
                       ['deployedHash']) = bytecode_hash

            (self._json['contracts']
                       [contract_idx]
                       ['networks']
                       [network_id]
                       ['deployedInstances']).append(
                           AttrDict({
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
    def account_known(self, address: str) -> bool:
        """ Check if an account is known """
        if (not self._json
                or self._json.get('seenAccounts') is None
                or type(self._json['seenAccounts']) != list):
            return False

        try:
            self._json['seenAccounts'].index(normalize_address(address))
            return True
        except ValueError:
            return False

    @autoload
    @autosave
    def add_account(self, address: str) -> None:
        """ Add an account to seenAccounts """

        if self._json is None:
            raise Exception("Invalid configuration. Corrupted file?")

        address = normalize_address(address)

        if not self._json.get('seenAccounts'):
            self._json['seenAccounts'] = []

        if self.account_known(address):
            return

        self._json['seenAccounts'].append(address)

    @autoload
    @autosave
    def set_default_account(self, address) -> None:
        """ Set the default account """

        if self._json is None:
            raise Exception("Invalid configuration. Corrupted file?")

        address = normalize_address(address)

        # Make sure we know about it
        self.add_account(address)

        self._json['defaultAccount'] = address

    @autoload
    def get_default_account(self) -> Optional[str]:
        """ Get the default account """

        if self._json is None:
            raise Exception("Invalid configuration. Corrupted file?")

        return self._json.get('defaultAccount')

    @autoload
    def cleanup(self, dry_run: bool = False) -> List[Tuple[str, str, str]]:
        """ Cleanup metafile.json of test deployments.  In practice, this means any deployments with
            a network_id > 100, as the last semi-official network_id is 99.

            Returns a list of tuple.  Tuples are (name, network_id).
        """
        if self._json is None or 'contracts' not in self._json or len(self._json['contracts']) < 1:
            return []

        removed: List = []

        contract_idx = 0
        for contract in self._json['contracts']:

            if 'networks' in contract and len(contract['networks']) > 0:
                keys_to_del = []

                # We can't alter the dict while iterating it, so get the IDs together first
                for net_id, depl in contract['networks'].items():
                    if int(net_id) > NETWORK_ID_MAX_OFFICIAL:
                        keys_to_del.append(net_id)

                if len(keys_to_del) > 0:
                    for net_id in keys_to_del:

                        removed += [(contract['name'], net_id) for net_id in keys_to_del]

                        if not dry_run:
                            self._json['contracts'][contract_idx]['networks'].pop(net_id)

                        log.debug(("(Probably) removed metafile entries for contract {} "
                                  "deployments on network {}.").format(
                            contract['name'],
                            net_id
                        ))
            else:
                log.debug("No deployments for contract {}".format(contract.get('name')))

            contract_idx += 1

        if len(removed) > 0:
            self._save()
            log.debug("Successfully cleaned up metafile.json.")
            return removed

        log.debug("Nothing to cleanup.")
        return removed

    def backup(self, outfile) -> bool:
        """ Backup the metafile.json and verify """
        if not isinstance(outfile, Path):
            outfile = Path(outfile)

        if not outfile.parent.exists():
            raise FileNotFoundError('Directory {} does not exist.'.format(outfile.parent))

        log.debug("Backup up metafile.json from {} to {}...".format(self.file_name, outfile))

        original_hash = hash_file(self.file_name)

        copyfile(self.file_name, outfile)

        backup_hash = hash_file(outfile)

        try:
            assert original_hash == backup_hash
            return True
        except AssertionError:
            log.error("Backup failed.  File mismatch!")
            return False
