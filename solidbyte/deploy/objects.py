""" Contract deployer """
import sys
from typing import TYPE_CHECKING, Union, Any, Optional, Dict, List, Tuple, Set
from attrdict import AttrDict
from getpass import getpass
from eth_utils.exceptions import ValidationError
from web3.eth import Contract as Web3Contract
from ..accounts import Accounts
from ..compile import link_library, clean_bytecode
from ..compile.artifacts import contract_artifacts
from ..compile.linker import hash_linked_bytecode
from ..common import pop_key_from_dict
from ..common.web3 import (
    web3c,
    normalize_hexstring,
    create_deploy_tx,
)
from ..common import store
from ..common.exceptions import DeploymentError, DeploymentValidationError
from ..common.logging import getLogger

# datetime.fromisoformat() isn't available until Python 3.7.  Monkeypatch!
if sys.version_info[0] == 3 and sys.version_info[1] < 7:
    from ..common.utils import Py36Datetime as datetime
else:
    from datetime import datetime

if TYPE_CHECKING:
    from ..common.metafile import MetaFile
    from web3 import Web3

log = getLogger(__name__)

# Typing
T = Union[Any, None]
MultiDict = Union[AttrDict, dict]

MAX_OFFICIAL_NETWORK_ID = 100
DISABLED_REMOTE_NOTICE = (
    "Deployment with remote accounts is currently disabled. If you're interested in having this "
    "enabled, please add your feedback to this issue: "
    "https://github.com/mikeshultz/solidbyte/issues/32"
)
ROOT_LEAF_NAME = "__root__"


def get_lineage(leaf: 'ContractLeaf') -> Set['ContractLeaf']:
    """ Climb a deptree and return all elements "above" the provided leaf """
    _parents: Set['ContractLeaf'] = set()
    if not leaf.parent or leaf.parent.name == ROOT_LEAF_NAME:
        return _parents
    else:
        _parents.add(leaf.parent)
        _parents.update(get_lineage(leaf.parent))
    return _parents


class ContractLeaf:
    """ A leaf object in the dependency tree

    :Definitions:
     - dependent: Leaves that this leaf depends on
     - dependency: A leaf that depends on this leaf
    """
    def __init__(self, name: str, tree: 'ContractDependencyTree',
                 parent: 'ContractLeaf' = None) -> None:

        self.name = name
        self.tree = tree
        self.parent = parent
        self.dependents: Set['ContractLeaf'] = set()

    def __repr__(self) -> str:
        return self.name

    def add_dependent(self, name: str) -> 'ContractLeaf':
        """ Add a dependent leaf """

        # If this element already exists, move it to be our dependent
        el, _ = self.tree.search_tree(name)
        if el is not None:
            self.tree.move(name, self)
            return el

        # Otherwise, create a new elemenet
        new_leaf = ContractLeaf(name, self.tree, self)
        self.dependents.add(new_leaf)
        return new_leaf

    def attach_dependent(self, el: 'ContractLeaf') -> None:
        """ Attach an element to this Leaf as dependent """
        self.dependents.add(el)

    def get_parent(self) -> Optional['ContractLeaf']:
        """ Return the parent ContractLeaf """
        return self.parent

    def is_root(self) -> bool:
        """ Is this the root leaf? """
        return self.parent is None

    def has_dependencies(self) -> bool:
        """ Does this leaf have dependencies? """
        return self.parent is not None and self.parent.name != ROOT_LEAF_NAME

    def has_dependents(self) -> bool:
        """ Does this leaf have dependents """
        return len(self.dependents) > 0

    def get_dependents(self) -> Set['ContractLeaf']:
        """ Resolve and return all dependents in a flat set """
        _dependents: Set['ContractLeaf'] = self.dependents
        for d in self.dependents:
            if d.has_dependents():
                _dependents.update(d.get_dependents())
        return _dependents

    def get_dependencies(self) -> Set['ContractLeaf']:
        """ Resolve and return all dependencies in a flat set """
        return get_lineage(self)


class ContractDependencyTree:
    """ A tree of Leafs describing contract library dependencies

    :Example:

    >>> deptree = ContractDependencyTree()
    """
    def __init__(self):
        self.root = ContractLeaf(ROOT_LEAF_NAME, self)

    def __repr__(self):
        strong = '[root]\n'
        for el in self.root.dependents:
            strong += '- {} (Dependants: {}, Has Dependencies: {})\n'.format(
                el,
                el.get_dependents(),
                el.has_dependencies()
            )
        return strong

    def _search(self, name: str, el: ContractLeaf = None,
                depth: int = 0) -> Tuple[Optional[ContractLeaf], int]:
        """ Internal recursive tree search function

        :param name: The name of the leaf to look for
        :param el: The current leaf to search down from; for recursive use
        :param depth: depth tracking, for recursive use
        """
        if el is None:
            el = self.root
            depth = -1
        if el.name == name:
            return (el, depth)
        else:
            found = None
            for dep in el.dependents:
                found, found_depth = self._search(name, dep, depth+1)
                if found:
                    return (found, found_depth)
            return (None, depth)

    def search_tree(self, name: str) -> Tuple[Optional[ContractLeaf], int]:
        """ Search a tree for a named leaf

        :param name: The name of the leaf to look for
        """
        return self._search(name)

    def has_dependents(self, name: str):
        """ Check of name has dependents """
        el, _ = self.search_tree(name)
        if el and len(el.dependents) > 0:
            return True
        return False

    def has_dependencies(self, name: str):
        """ Check of name has dependencies """
        el, depth = self.search_tree(name)
        if el and depth > 0:
            return True
        return False

    def add_dependent(self, name: str, parent: str = None) -> ContractLeaf:
        """ Add a child dependent """
        if parent:
            el, _ = self.search_tree(parent)
        if el is None:
            el = self.root
        return el.add_dependent(name)

    def move(self, name: str, new_parent: ContractLeaf) -> ContractLeaf:
        """ Move an element to be a child of another """
        el, _ = self.search_tree(name)
        if el is None or el.parent is None:
            raise Exception('Element to move was not found')
        el.parent.dependents.remove(el)
        new_parent.attach_dependent(el)
        el.parent = new_parent
        return el


class Deployment:
    """ representation of a simgle contract deployment """
    def __init__(self, network: str, address: str, bytecode_hash: str, date: datetime,
                 abi: List[Dict[str, T]]):
        self.network = network
        self.address = address
        self.bytecode_hash = bytecode_hash
        self.date = date
        self.abi = abi


class Contract:
    """ The representation of a smart contract deployment state on a specific network.

    This object is exposed to users' in their deploy script, instantiated for each of their
    contracts.  The general use is to provide information about the contract state, a Web3 Contract
    instance and deploy it if necessary.  There's a bunch of properties, but two primary methods to
    interact with the contract.

    * check_needs_deployment(bytecode: str) -> bool: This function will take the provided bytecode
        and return whether or not there's been a change compared to the known, deployed bytecode.

    * deployed(*args: T, **kwargs: T) -> web3.eth.Contract: This is the primary interaction a user
        has with this object in a deploy script.  It will return an instantiated web3.eth.Contract
        instance and in the process, deploy the smart contract if necessary.
    """
    def __init__(self, name: str, network_name: str, from_account: str,
                 metafile: 'MetaFile', web3: 'Web3' = None):
        """ Initialize the Contract

        :param name: The name of... me.  The name of the contract I represent.
        :param network_name: The name of of the network, as defined in networks.yml.
        :param from_account: The address of the account to deploy with.
        :param metafile: An instantiated MetaFile object.
        :param web3: An instantiated Web3 object

        :Example:

        >>> from solidbyte.deploy.objects import Contract
        >>> MyContract = Contract(
        ...         'TestContract',
        ...         'test',
        ...         '0xdeadbeef00000000000000000000000000000000',
        ...         MetaFile(),
        ...         Web3(),
        ... )
        >>> my_contract = MyContract.deployed()

        """

        log.debug("Contract.__init__({}, {}, {}, {}, {})".format(name, network_name,
                                                                 from_account, metafile, web3))

        self.name = name
        self.new_deployment = False
        self.deployedHash = None
        self.source_bytecode = None
        self.source_abi = None
        self.links = None  # This will only populate after a _deploy()
        self.deployments: List = []
        self.from_account = from_account
        if web3:
            self.web3 = web3
        else:
            self.web3 = web3c.get_web3(network_name)
        self.network_id = self.web3.net.chainId or self.web3.net.version
        self.accounts = Accounts(web3=self.web3)
        self.metafile = metafile

        self.refresh()

    def __repr__(self) -> str:
        return self.name

    @property
    def address(self) -> Optional[str]:
        """ The latest deployed address """
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].address

    @property
    def abi(self) -> Optional[List[Dict[str, T]]]:
        """ The latest deployed ABI """
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].abi

    @property
    def bytecode_hash(self)-> Optional[str]:
        """ The latest deployed bytecode hash """
        if len(self.deployments) < 1:
            return None
        return self.deployments[-1].bytecode_hash

    def is_deployed(self) -> bool:
        """ Return if this contract has deployments """
        return len(self.deployments) > 0

    def refresh(self) -> None:
        """ Refresh metadata from MetaFile and the compiled artifacts """
        self._load_metafile_contract()
        self._load_artifacts()

    def check_needs_deployment(self, bytecode: str) -> bool:
        """ Check if this contract has been changed since last deployment

        **NOTE**: This method does not take into account dependencies.  Check with Deployer

        :param bytecode: The hex bytecode to compare to the latest known deployment.
        :returns: If the bytecode differs from the last known deployment.

        :Example:

        >>> from solidbyte.deploy.objects import Contract
        >>> MyContract = Contract('test', '0xdeadbeef00000000000000000000000000000000', {
        ...         'abi': [],
        ...         'bytecode': '0x1234...'
        ...         'name': 'MyContract'
        ...     }, {}, MetaFile())
        >>> assert Mycontract.check_needs_deployment('0x2234...')

        """

        if not bytecode:
            raise DeploymentValidationError("bytecode is required")

        bytecode_hash = hash_linked_bytecode(bytecode)

        self.refresh()

        return (
            not self.bytecode_hash
            or bytecode_hash != self.bytecode_hash
        )

    def deployed(self, *args, **kwargs):
        """ Return an instantiated web3.eth.Contract tinstance and deploy the contract if necessary.

        :param *args: Any args to provide the constructor.
        :param **kargs: Any kwargs to provide the constructor OR one of the following special
            kwargs:
            - gas: The gas limit for the deploy transaction.
            - gas_price: The gas price to use, in wei.
            - links: This is a dict of {name,address} of library links for the contract.
        :returns: If the bytecode differs from the last known deployment.

        :Example:

        >>> from solidbyte.deploy.objects import Contract
        >>> MyContract = Contract('test', '0xdeadbeef00000000000000000000000000000000', {
        ...         'abi': [],
        ...         'bytecode': '0x1234...'
        ...         'name': 'MyContract'
        ...     }, {}, MetaFile())
        >>> contract = Mycontract.deploy(links={
                    'MyLibrary': '0xdeadbeef00000000000000000000000000000001'
                })
        >>> assert contract.functions.owner().call() == contract.from_account

        """

        if not self.check_needs_deployment(self.source_bytecode):
            return self._get_web3_contract()

        try:
            return self._deploy(*args, **kwargs)
        except Exception as e:
            log.exception("Unknown error deploying {}".format(self.name))
            raise e

    def _process_instances(self, metafile_instances: List[Dict[str, T]]) -> None:
        """ Process the deployedInstances dict for this contract from the metafile.

        :param metafile_instances: A list of deployedInstances from metafile.json.
        """
        self.deployments: List[Deployment] = []
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

    def _load_metafile_contract(self) -> None:
        """ Process the contract dict for this contract from the metafile. """

        metafile_contract = self.metafile.get_contract(self.name)

        if not metafile_contract:
            log.debug('No metafile.json entry for contract {}.'.format(self.name))
            return

        if metafile_contract['networks'].get(self.network_id):

            self.deployedHash = metafile_contract['networks'][self.network_id].get('deployedHash')
            deployed_instances = metafile_contract['networks'][self.network_id].get(
                'deployedInstances'
            )

            if deployed_instances and len(deployed_instances) > 0:

                self._process_instances(
                        metafile_contract['networks'][self.network_id]['deployedInstances']
                    )

    def _load_artifacts(self) -> None:
        """ Process the artifact dict from metafile.json. """
        source = contract_artifacts(self.name)
        if source:
            self.name = source['name']
            self.source_abi = source['abi']
            self.source_bytecode = normalize_hexstring(source['bytecode'])

    def _create_deploy_transaction(self, bytecode: str, gas: int, gas_price: int,
                                   *args, **kwargs) -> dict:
        """ Create the transaction to deploy the contract

        :param bytecode: The bytecode we're deploying.
        :param gas: The gas limit for the transaction.
        :param gas_price: The gas price in wei for the transaction.
        :param *args: Constructor arguments
        :param **kargs: Constructor keyword arguments
        :returns: a transaction dict from Web3
        """

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

    def _transact(self, tx: MultiDict) -> str:
        """ Execute the deploy transaction

        :param tx: The transaction dict.
        :returns: A transaction hash.
        """

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
                    passphrase = store.get(store.Keys.DECRYPT_PASSPHRASE)
                    if not passphrase:
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

        log.debug("Deployment transaction hash for {}: {}".format(self.name, deploy_txhash.hex()))

        return deploy_txhash.hex()

    def _assemble_and_hash_bytecode(self, bytecode: str,
                                    links: Optional[dict] = None) -> Tuple[str, str]:
        """ Link bytecode(if necessary), and hash in a way that links are irrelevant

        :param bytecode: The bytecode from compiler output
        :param links: A dict with links(key: contract name, value: deployed address).
        :returns: A Tuple of the bytecode hash and linked bytecode.
        """

        bytecode_hash = hash_linked_bytecode(bytecode)  # Hash before linking

        if links:
            bytecode = link_library(bytecode, links)

        return (bytecode_hash, clean_bytecode(bytecode))

    def _deploy(self, *args, **kwargs) -> Web3Contract:
        """ Deploy the contract

        :param *args: Any args to provide the constructor.
        :param **kargs: Any kwargs to provide the constructor OR one of the following special
            kwargs:
            - gas: The gas limit for the deploy transaction.
            - gasPrice: The gas price to use, in wei.
            - links: This is a dict of {name,address} of library links for the contract.
        :returns: A instantiated web3.eth.Contract object.
        """

        self.links = pop_key_from_dict(kwargs, 'links')
        bytecode_hash, bytecode = self._assemble_and_hash_bytecode(self.source_bytecode, self.links)
        assert len(bytecode_hash) == 66, "Invalid response from linker."  # Just in case. Got bit.

        gas = pop_key_from_dict(kwargs, 'gas') or int(6e6)
        gas_price = (
            pop_key_from_dict(kwargs, 'gasPrice')
            or pop_key_from_dict(kwargs, 'gas_price')
            or self.web3.toWei('3', 'gwei')
        )

        assert type(gas) == int and type(gas_price) == int, (
            "Invalid gas or gas_price type. Expected (<class 'int'>/<class 'int'>) "
            "got ({}/{})".format(
                type(gas), type(gas_price)
            ))

        max_fee_wei = gas * gas_price
        deployer_balance = self.web3.eth.getBalance(self.from_account)

        log.debug("Max network fee: {} ({} Ether)".format(
                max_fee_wei,
                self.web3.fromWei(max_fee_wei, 'ether')
            ))
        log.debug("Deployer balance: {} ({})".format(deployer_balance, self.from_account))

        if deployer_balance < max_fee_wei:
            raise DeploymentValidationError(
                    "Deployer account {} under-funded! Has: {} Needed: {}".format(
                        self.from_account,
                        deployer_balance,
                        max_fee_wei,
                    )
                )

        log.debug("Creating deploy transaction...")
        deploy_tx = self._create_deploy_transaction(bytecode, gas, gas_price, *args, **kwargs)

        deploy_txhash = self._transact(deploy_tx)

        log.info("Sending deploy transaction {} for contract {}.  This may take a moment...".format(
            deploy_txhash,
            self.name,
        ))

        # Wait for it to be mined
        deploy_receipt = self.web3.eth.waitForTransactionReceipt(deploy_txhash)

        # Verify all the things
        if deploy_receipt.status == 0:
            log.info("Receipt: {}".format(deploy_receipt))
            raise DeploymentError("Deploy transaction failed!")

        log.debug("Contract Deploy Receipt: {}".format(deploy_receipt))

        code = self.web3.eth.getCode(deploy_receipt.contractAddress)
        if not code or code == '0x':
            raise DeploymentError(
                "Bytecode for {} not found at address {}.  This could mean the node is out "
                "of sync or that deployment failed for an unknown reason.".format(
                    self.name,
                    deploy_receipt.contractAddress,
                )
            )

        log.info("Successfully deployed {}. Transaction has been mined.".format(self.name))

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

        self.new_deployment = True

        log.debug("Updated metadata for new deployment.")

        return self._get_web3_contract()

    def _get_web3_contract(self) -> Web3Contract:
        """ Instantiate a web3.eth.Contract instance with their factory and return.

        :returns: A instantiated web3.eth.Contract object.
        """
        assert self.abi is not None, "ABI appears to be missing for contract {}".format(self.name)
        assert self.address is not None, "Address appears to be missing for contract {}".format(
                self.name
            )
        return self.web3.eth.contract(abi=self.abi, address=self.address)
