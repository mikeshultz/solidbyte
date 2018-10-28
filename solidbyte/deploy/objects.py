""" Contract deployer """
from datetime import datetime
from ..accounts import Accounts
from ..common.web3 import (
    web3c,
    hash_hexstring,
    create_deploy_tx,
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
    def __init__(self, network_name, from_account, source_contract=None, metafile_contract=None, metafile=None):
        self.name = None
        self.deployedHash = None
        self.source_bytecode = None
        self.source_abi = None
        self.from_account = from_account
        self.metafile = metafile
        self.web3 = web3c.get_web3(network_name)
        self.network_id = self.web3.net.chainId or self.web3.net.version
        self.accounts = Accounts()
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
        last_date = None
        latest_address = None
        for inst in metafile_instances:
            # We want the latest deployed address for the active network
            if inst.get('date') > last_date:
                latest_address = inst.get('address')
                last_date = inst.get('date')

            self.deployments.append(Deployment(
                bytecode_hash=inst.get('hash'),
                date=inst.get('date'),
                address=inst.get('address'),
                network=inst.get('network_id'),
                abi=inst.get('abi'),
                ))

        self.address = latest_address

    def _process_metafile_contract(self, metafile_contract):
        self.name = metafile_contract.get('name')

        if metafile_contract.networks.get(self.network_id):
            self.deployedHash = metafile_contract.networks[self.network_id].get('deployedHash')
            
            if metafile_contract.networks[self.network_id].get('deployedInstances') \
                and len(metafile_contract.networks[self.network_id]['deployedInstances']) > 0:

                self._process_instances(metafile_contract.networks[self.network_id]['deployedInstances'])

    def _process_source_contract(self, source):
        self.name = source.name
        self.source_abi = source.abi
        self.source_bytecode = source.bytecode

    def _deploy(self, *args, **kwargs):
        """ Deploy the contract """

        nonce = self.web3.eth.getTransactionCount(self.from_account)
        # Create the tx object
        deploy_tx = create_deploy_tx(self.source_abi, self.source_bytecode, {
             'chainId': int(self.network_id),
             'gas': int(3e6), # TODO: We need to be able to adjust these
             'gasPrice': self.web3.toWei('3', 'gwei'),
             'nonce': nonce,
             'from': self.from_account,
            }, *args, **kwargs)

        # Sign it
        signed_tx = self.accounts.sign_tx(self.from_account, deploy_tx)

        # Send it
        deploy_txhash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        # Wait for it to be mined
        deploy_receipt = self.web3.eth.waitForTransactionReceipt(deploy_txhash)
        
        bytecode_hash = hash_hexstring(self.source_bytecode)
        self.deployments.append(Deployment(
                bytecode_hash=bytecode_hash,
                date=datetime.now().isoformat(),
                address=deploy_receipt.contractAddress,
                network=self.network_id,
                abi=self.source_abi,
                ))
        self.metafile.add(self.name, self.network_id, deploy_receipt.contractAddress, self.source_abi, bytecode_hash)
        return self._get_web3_contract()

    def _get_web3_contract(self):
        """ Return the web3.py contract instance """
        assert self.abi is not None, "ABI appears to be missing for contract {}".format(self.name)
        assert self.address is not None, "Address appears to be missing for contract {}".format(self.name)
        return self.web3.eth.contract(abi=self.abi, address=self.address)

    def deployed(self, *args, **kwargs):
        """ If necessary, deploy the new script """

        if not self.check_needs_deployment(self.source_bytecode):
            return self._get_web3_contract()

        try:
            return self._deploy(*args, **kwargs)
        except Exception as e:
            log.exception("Unknown error deploying contract")
            raise e
