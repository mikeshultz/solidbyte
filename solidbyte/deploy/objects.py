""" Contract deployer """
import binascii
from datetime import datetime
from attrdict import AttrDict
from getpass import getpass
from eth_utils.exceptions import ValidationError
from ..accounts import Accounts
from ..compile import link_library, clean_bytecode
from ..common import pop_key_from_dict
from ..common.web3 import (
    web3c,
    normalize_hexstring,
    hash_string,
    create_deploy_tx,
)
from ..common.exceptions import DeploymentError, DeploymentValidationError
from ..common.logging import getLogger

log = getLogger(__name__)

MAX_OFFICIAL_NETWORK_ID = 100
DISABLED_REMOTE_NOTICE = (
    "Deployment with remote accounts is currently disabled. If you're interested in having this "
    "enabled, please add your feedback to this issue: "
    "https://github.com/mikeshultz/solidbyte/issues/32"
)


class Deployment(object):
    def __init__(self, network, address, bytecode_hash, date, abi):
        self.network = network
        self.address = address
        self.bytecode_hash = bytecode_hash
        self.date = date
        self.abi = abi


class Contract(object):
    def __init__(self, network_name, from_account, source_contract=None, metafile_contract=None,
                 metafile=None):
        self.name = None
        self.deployedHash = None
        self.source_bytecode = None
        self.source_abi = None
        self.from_account = from_account
        self.metafile = metafile
        self.web3 = web3c.get_web3(network_name)
        self.network_id = self.web3.net.chainId or self.web3.net.version
        self.accounts = Accounts(web3=self.web3)
        self.deployments = []
        if metafile_contract:
            if type(metafile_contract) == dict:
                metafile_contract = AttrDict(metafile_contract)
            self._process_metafile_contract(metafile_contract)
        if source_contract:
            self._process_source_contract(source_contract)

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
    def bytecode_hash(self):
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].bytecode_hash

    def check_needs_deployment(self, bytecode):
        log.debug("{}.check_needs_deployment({})".format(
            self.name,
            bytecode
        ))
        if not bytecode:
            raise Exception("bytecode is required")
        return (
            not self.bytecode_hash
            or hash_string(clean_bytecode(bytecode)) != self.bytecode_hash
        )

    def _process_instances(self, metafile_instances):
        """ Process the deployedInstances object for that contract from the
            metafile.
        """
        self.deployments = []
        last_date = None
        for inst in metafile_instances:
            # We want the latest deployed address for the active network
            if inst.get('date'):
                this_date = datetime.fromisoformat(inst['date'])
                if last_date is None or this_date > last_date:
                    last_date = this_date

            self.deployments.append(Deployment(
                bytecode_hash=inst.get('hash'),
                date=this_date,
                address=inst.get('address'),
                network=inst.get('network_id'),
                abi=inst.get('abi'),
                ))

    def _process_metafile_contract(self, metafile_contract):
        self.name = metafile_contract.get('name')

        if metafile_contract.networks.get(self.network_id):
            self.deployedHash = metafile_contract.networks[self.network_id].get('deployedHash')

            if metafile_contract.networks[self.network_id].get('deployedInstances') \
                    and len(metafile_contract.networks[self.network_id]['deployedInstances']) > 0:

                self._process_instances(
                        metafile_contract.networks[self.network_id]['deployedInstances']
                    )

    def _process_source_contract(self, source):
        self.name = source.name
        self.source_abi = source.abi
        self.source_bytecode = normalize_hexstring(source.bytecode)

    def _create_deploy_transaction(self, bytecode, gas, gas_price, *args, **kwargs):
        """ Create the transaction to deploy the contract """

        nonce = self.web3.eth.getTransactionCount(self.from_account)

        # Create the tx object
        deploy_tx = create_deploy_tx(self.web3, self.source_abi, bytecode, {
             'chainId': int(self.network_id),
             'gas': gas,
             'gasPrice': gas_price,
             'nonce': nonce,
             'from': self.from_account,
            }, *args, **kwargs)

        return deploy_tx

    def _transact(self, tx):
        """ Execute the deploy transaction """

        if self.accounts.account_known(self.from_account):

            # Sign it
            signed_tx = self.accounts.sign_tx(self.from_account, tx)

            # Send it
            try:
                deploy_txhash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            except (
                ValidationError,
                ValueError,
            ) as err:
                str_err = str(err)
                if 'out of gas' in str_err or 'exceeds gas' in str_err:
                    log.error('TX ran out of gas when deploying {}.'.format(self.name))
                elif 'cannot afford txn gas' in str_err:
                    log.error('Deployer account unable to afford network fees')
                log.debug(tx)
                log.debug({k: v for k, v in signed_tx.items()})
                raise err

        else:

            if int(self.network_id) < MAX_OFFICIAL_NETWORK_ID and not self.web3.is_eth_tester:
                """ Disabling personal.unlock for official chains. It's not really a secure way to
                    deal with sending transactions. At least on go-ethereum, when you unlock an
                    account, that allows any party that can send a JSON-RPC request to the node to
                    send transactions on that acocunt's behalf.  If the machine isn't strictly local
                    or firewalled in some way to prevent malicious parties from communicating with
                    it (rare), that leaves the account easily compromised once unlocked.

                    If you want to disagree or call me an idiot, please do:
                        https://github.com/mikeshultz/solidbyte/issues/32
                """
                raise DeploymentValidationError(DISABLED_REMOTE_NOTICE)
            else:
                tx['from'] = self.from_account
                if self.web3.is_eth_tester:
                    deploy_txhash = self.web3.eth.sendTransaction(tx)
                else:
                    # TODO: maybe incorporate this into Accounts?
                    passphrase = getpass("Enter password to unlock account ({}):".format(
                        self.from_account
                    ))
                    if self.web3.personal.unlockAccount(self.from_account, passphrase,
                                                        duration=60*5):
                        deploy_txhash = self.web3.eth.sendTransaction(tx)
                    else:
                        raise DeploymentError("Unable to unlock account {}".format(
                            self.from_account
                        ))

        return deploy_txhash

    def _deploy(self, *args, **kwargs):
        """ Deploy the contract """

        bytecode = self.source_bytecode
        kwargs, links = pop_key_from_dict(kwargs, 'links')
        if links is not None:
            bytecode = link_library(self.source_bytecode, links)

        # TODO: The user needs to be able to adjust these
        gas = int(6e6)
        gas_price = self.web3.toWei('3', 'gwei')
        max_fee_wei = gas * gas_price
        deployer_balance = self.web3.eth.getBalance(self.from_account)

        log.debug("Max network fee: {} ({} Ether)".format(
                max_fee_wei,
                self.web3.fromWei(max_fee_wei, 'ether')
            ))
        log.debug("Deployer balance: {}".format(deployer_balance))

        if deployer_balance < max_fee_wei:
            raise DeploymentValidationError(
                    "Deployer account {} under-funded! Has: {} Needed: {}".format(
                        self.from_account,
                        deployer_balance,
                        max_fee_wei,
                    )
                )

        log.debug("Sending deploy transaction...")
        deploy_tx = self._create_deploy_transaction(bytecode, gas, gas_price, *args, **kwargs)

        log.info("Sending deploy transaction.  This may take a moment...")
        deploy_txhash = self._transact(deploy_tx)

        # Wait for it to be mined
        deploy_receipt = self.web3.eth.waitForTransactionReceipt(deploy_txhash)

        log.info("Successfully deployed contract. {}".format(deploy_txhash))
        log.debug("Contract Deploy Receipt: {}".format(deploy_receipt))

        # TODO: Should this take into account a library address changing? (using linked bytecode?)
        bytecode_hash = None
        try:
            bytecode_hash = hash_string(clean_bytecode(self.source_bytecode))
        except binascii.Error as err:
            log.exception("Invalid characters in hex string: {}".format(
                clean_bytecode(self.source_bytecode))
            )
            raise err

        self.deployments.append(Deployment(
                bytecode_hash=bytecode_hash,
                date=datetime.now().isoformat(),
                address=deploy_receipt.contractAddress,
                network=self.network_id,
                abi=self.source_abi,
            ))

        self.metafile.add(self.name, self.network_id,
                          deploy_receipt.contractAddress, self.source_abi,
                          bytecode_hash)

        log.info("Updated metadata for new deployment.")

        return self._get_web3_contract()

    def _get_web3_contract(self):
        """ Return the web3.py contract instance """
        assert self.abi is not None, "ABI appears to be missing for contract {}".format(self.name)
        assert self.address is not None, "Address appears to be missing for contract {}".format(
                self.name
            )
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
