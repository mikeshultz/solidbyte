""" Ethereum deployment functionality """
import json
from os import path, getcwd, listdir
from ..common import builddir, source_filename_to_name
from ..common.logging import getLogger
from ..common.web3 import (
    web3,
    hash_hexstring,
    deploy_contract,
    normalize_address,
    normalize_hexstring,
)
from .metafile import MetaFile

log = getLogger(__name__)

def get_latest_from_deployed(deployed_instances, deployed_hash):
    return list(filter(lambda x: x['hash'] == deployed_hash, deployed_instances))[0]

class Contracts(object):

    def __init__(self, contract_dir=None):
        self.contracts_dir = contract_dir or path.join(getcwd(), 'contracts')
        self.builddir = builddir()
        self.contracts = {}
        self.metafile = MetaFile()

    def get_contracts(self):
        contract_files = [f for f in listdir(self.contracts_dir) if path.isfile(path.join(self.contracts_dir, f))]
        for contract in contract_files:
            name = source_filename_to_name(contract)

            abi_filename = path.join(self.builddir, name, '{}.abi'.format(name))
            with open(abi_filename, 'r') as abi_file:
                abi = json.loads(abi_file.read())

            bytecode_filename = path.join(self.builddir, name, '{}.bin'.format(name))
            with open(bytecode_filename, 'r') as bytecode_file:
                bytecode = bytecode_file.read()

            self.contracts[name] = (abi, bytecode)

        return self.contracts

    def get_deployed_contracts(self):
        return self.metafile.get_all_contracts()

    def deploy(self, name, contract_tuple):
        abi, bytecode = contract_tuple
        bytecode_hash = hash_hexstring(bytecode)

        if not bytecode:
            log.warning("Not deploying {} because bytecode is 0 length".format(name))
            return

        log.info("Deploying {}...".format(name))

        meta = self.metafile.get_contract(name)

        if meta:
            if bytecode_hash == meta.get('deployedHash'):
                log.info("Skipping deployment of {}. No changes.".format(name))
                return None
        
        log.info("Deploying new version of {}...".format(name))

        contract_instance = deploy_contract(abi, bytecode)
        self.metafile.add(name, contract_instance.address, bytecode_hash)

    def deploy_all(self):
        log.info("Deploying all contracts")
        
        self.get_contracts()

        for cname in self.contracts.keys():
            self.deploy(cname, self.contracts[cname])
