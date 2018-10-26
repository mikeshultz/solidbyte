""" Contract deployer """
from datetime import datetime
from ..common.web3 import (
    web3,
    hash_hexstring,
    deploy_contract,
)
from ..common.logging import getLogger

log = getLogger(__name__)

class Deployment(object):
    def __init__(self, network, address, bytecode_hash, date, abi):
        self.network = network
        self.address = address
        self.bytecode_hash = bytecode_hash,
        self.date = date
        self.abi = abi

class Contract(object):
    def __init__(self, source_contract=None, metafile_contract=None, metafile=None):
        self.name = None
        self.deployedHash = None
        self.source_bytecode = None
        self.source_abi = None
        self.metafile = metafile
        if metafile_contract:
            self._process_metafile_contract(metafile_contract)
        if source_contract:
            self._process_source_contract(source_contract)
        self.deployments = []

    def is_deployed(self): 
        return len(self.deployments) > 0

    @property
    def address(self):
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].address

    @property
    def abi(self):
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].abi

    @property
    def bytecode(self):
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].bytecode

    def check_needs_deployment(self, bytecode):
        log.debug("{}.check_needs_deployment({})".format(
            self.name,
            bytecode
        ))
        if not bytecode:
            raise Exception("bytecode is required")
        return (
            not self.bytecode \
            or hash_hexstring(bytecode) != hash_hexstring(self.bytecode)
        )

    def _process_instances(self, metafile_instances):
        """ Process the deployedInstances object for that contract from the
            metafile.
        """
        self.deployments = []
        for inst in metafile_instances:
            self.deployments.append(Deployment(
                bytecode_hash=inst.get('hash'),
                date=inst.get('date'),
                address=inst.get('address'),
                network=inst.get('network'),
                abi=inst.get('abi'),
                ))

    def _process_metafile_contract(self, metafile_contract):
        self.name = metafile_contract.get('name')
        self.deployedHash = metafile_contract.get('deployedHash')

        if metafile_contract.get('deployedInstances') \
            and len(metafile_contract['deployedInstances']) > 0:

            self._process_instances(metafile_contract['deployedInstances'])

    def _process_source_contract(self, source):
        self.name = source.name
        self.source_abi = source.abi
        self.source_bytecode = source.bytecode

    def _deploy(self, *args, **kwargs):
        """ Deploy the contract """
        addr = deploy_contract(self.source_abi, self.source_bytecode, *args, **kwargs)
        bytecode_hash = hash_hexstring(self.source_bytecode)
        self.deployments.append(Deployment(
                bytecode_hash=bytecode_hash,
                date=datetime.now().isoformat(),
                address=addr,
                network=1, # TODO: Support network
                abi=self.source_abi,
                ))
        self.metafile.add(self.name, addr, self.source_abi, bytecode_hash)
        return self._get_web3_contract()

    def _get_web3_contract(self):
        """ Return the web3.py contract instance """
        assert self.abi is not None, "ABI appears to be missing for contract {}".format(self.name)
        assert self.address is not None, "Address appears to be missing for contract {}".format(self.name)
        return web3.eth.contract(abi=self.abi, address=self.address)

    def deployed(self, *args, **kwargs):
        """ If necessary, deploy the new script """

        if not self.check_needs_deployment(self.source_bytecode):
            return self._get_web3_contract()

        try:
            return self._deploy(*args, **kwargs)
        except:
            log.exception("Error deploying contract")
            return None
