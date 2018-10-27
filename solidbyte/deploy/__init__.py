""" Ethereum deployment functionality """
import inspect
import json
from os import path, getcwd, listdir
from importlib import import_module
from importlib.machinery import SourceFileLoader
from pathlib import Path
from attrdict import AttrDict
from ..common import builddir, source_filename_to_name
from ..common.logging import getLogger
from ..common.web3 import (
    web3,
    hash_hexstring,
    deploy_contract,
    normalize_address,
    normalize_hexstring,
)
from ..common.metafile import MetaFile
from .objects import Contract

log = getLogger(__name__)

def get_latest_from_deployed(deployed_instances, deployed_hash):
    return list(filter(lambda x: x['hash'] == deployed_hash, deployed_instances))[0]

class Deployer(object):

    def __init__(self, contract_dir=None, deploy_dir=None):
        self.contracts_dir = contract_dir or path.join(getcwd(), 'contracts')
        self.deploy_dir = deploy_dir or path.join(getcwd(), 'deploy')
        self.builddir = builddir()
        self._contracts = AttrDict()
        self._source_contracts = AttrDict()
        self._deploy_scripts = []
        self.metafile = MetaFile()

        if not path.isdir(self.contracts_dir):
            raise FileNotFoundError("contracts directory does not exist")

    def get_source_contracts(self, force=False):

        # Load only if necessary or forced
        if not force and len(self._source_contracts) > 0:
            return self._source_contracts

        self._source_contracts = AttrDict()
        contract_files = [f for f in listdir(self.contracts_dir) if path.isfile(path.join(self.contracts_dir, f))]
        for contract in contract_files:
            name = source_filename_to_name(contract)

            log.debug("Loading contract: {}".format(name))

            abi_filename = path.join(self.builddir, name, '{}.abi'.format(name))
            with open(abi_filename, 'r') as abi_file:
                abi = json.loads(abi_file.read())

            bytecode_filename = path.join(self.builddir, name, '{}.bin'.format(name))
            with open(bytecode_filename, 'r') as bytecode_file:
                bytecode = bytecode_file.read()

            self._source_contracts[name] = AttrDict({
                'name': name,
                'abi': abi,
                'bytecode': bytecode,
            })

        return self._source_contracts
    source_contracts = property(get_source_contracts)

    @property
    def deployed_contracts(self):
        return self.metafile.get_all_contracts()

    def get_contracts(self, force=False):
        if len(self._contracts) > 0 and not force:
            return self._contracts

        self._contracts = AttrDict()
        for key in self.source_contracts.keys():
            contract = Contract(
                metafile_contract=self.deployed_contracts.get(key),
                source_contract=self.source_contracts[key],
                metafile=self.metafile,
            )
            self._contracts[key] = contract

        return self._contracts
    contracts = property(get_contracts)

    def _load_user_scripts(self):
        """ Load the user deploy scripts from deploy folder """
        script_dir = Path(self.deploy_dir)
        
        if not script_dir.is_dir():
            raise Exception("deploy directory does not appear to be a directory")

        for node in script_dir.iterdir():
            if node.is_file() \
                and node.name.startswith('deploy') \
                and node.name.endswith('.py'):
                try:
                    #mod = import_module('{}'.format(node.name[:-3]), package="deploy")
                    mod = SourceFileLoader(node.name[:-3], str(node)).load_module()
                    self._deploy_scripts.append(mod)
                except ModuleNotFoundError as e:
                    if str(e) == "No module named 'deploy'":
                        raise Exception("Unable to find deploy module.  Missing deploy/__init__.py?")
                    else:
                        raise e

    def _get_script_kwargs(self):
        """ Return the available kwargs to give to user scripts """
        return {
            'contracts': self.contracts
        }

    def refresh(self, force=True):
        return (
            self.get_source_contracts(force=force) \
            or self.get_contracts(force=force) \
            or self.deployed_contracts
        )

    def check_needs_deploy(self, name=None):
        """ Check if any contracts need to be deployed """

        if name is not None and not self.source_contracts.get(name):
            raise FileNotFoundError("Unknown contract: {}".format(name))
        
        # If we don't know about the contract from the metafile, it needs deploy
        if name is not None and not self.contracts.get(name):
            return True
        elif name is not None:
            newest_bytecode = self.source_contracts[name].bytecode
            self.contracts[name].check_needs_deployment(newest_bytecode)

        # If any known contract needs deployment, we need to deploy
        for key in self.contracts.keys():
            log.debug("Checking if contract {} needs deployment.".format(key))
            newest_bytecode = self.source_contracts[key].get('bytecode')
            if not newest_bytecode:
                log.warn("Bytecode is zero")
            elif newest_bytecode \
                and self.contracts[key].check_needs_deployment(newest_bytecode):
                return True

        return False

    def deploy(self):
        """ Deploy the contracts in some fashion lol """

        self._load_user_scripts()

        available_kwargs = self._get_script_kwargs()

        for script in self._deploy_scripts:
            """
            It should be be flexible for users to write their deploy scripts.
            They can pick and choose what kwargs they want to reeive.  To handle
            that, we need to inspect the function to see what they want, then 
            provide what we can.
            """
            spec = inspect.getargspec(script.main)
            script_kwargs = { k: available_kwargs.get(k) for k in spec.args }
            retval = script.main(**script_kwargs)
            if retval != True:
                raise Exception("Deploy script did not complete properly!")

        return True
