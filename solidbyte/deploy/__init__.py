""" Ethereum deployment functionality """
import inspect
from typing import Optional, Union, Any, List, Dict, Set
from importlib.machinery import SourceFileLoader
from pathlib import Path
from attrdict import AttrDict
from ..compile.linker import bytecode_link_defs
from ..compile.artifacts import artifacts
from ..common import (
    builddir,
    to_path_or_cwd,
)
from ..common.exceptions import AccountError, DeploymentError
from ..common.logging import getLogger
from ..common.web3 import web3c
from ..common.metafile import MetaFile
from ..common.networks import NetworksYML
from .objects import Contract, ContractDependencyTree

log = getLogger(__name__)

# Typing
T = Union[Any, None]
PS = Union[Path, str]
MultiDict = Union[AttrDict, dict]


def get_latest_from_deployed(deployed_instances: MultiDict, deployed_hash: str) -> MultiDict:
    """ Quick filter function to pull the deployed instance from deployedInstances from a metafaile.

    :param deployed_instances: The deployedInstances from a metafile contract
    :param deployed_hash: A deployedHash from that same object
    """
    if deployed_instances is None or deployed_hash is None:
        return None
    return list(filter(lambda x: x['hash'] == deployed_hash, deployed_instances))[0]


class Deployer:
    """ The big ugly black box of an object that handles deployment in one giant muddy process but
    it tries to be useful to various parts of the system and represent the current state of the
    entire project's deployments.

    The primary purpose of this object is to know if a deployment is necessary, and to handle the
    deployment of all contracts if necessary.

    :Example:

    >>> from solidbyte.deploy import Deployer
    >>> d = Deployer('test', '0xdeadbeef00000000000000000000000000000000',
                     Path('/path/to/my/project'))
    >>> assert d.check_needs_deploy() == True
    >>> d.deploy()

    """
    def __init__(self, network_name: str, account: str = None, project_dir: PS = None):
        """ Initialize the Deployer. Get it juiced up.  Make the machine shudder.

        :param network_name: The name of of the network, as defined in networks.yml.
        :param account: The address of the account to deploy with.
        :param project_dir: The project directory, if not pwd.
        """
        self._deploy_scripts: List = []
        self.network_name = network_name
        self.deptree: Optional[ContractDependencyTree] = None
        self.project_dir = to_path_or_cwd(project_dir)
        self.contracts_dir = self.project_dir.joinpath('contracts')
        self.deploy_dir = self.project_dir.joinpath('deploy')
        self.builddir = builddir(self.project_dir)
        self._contracts = AttrDict()
        self._artifacts = AttrDict()
        self.web3 = web3c.get_web3(network_name)
        self.network_id = self.web3.net.chainId or self.web3.net.version

        # yml = NetworksYML(project_dir=self.project_dir)
        # if yml.is_eth_tester(network_name):
        #     self.metafile: MetaFile = MetaFile(project_dir=project_dir, read_only=True)
        # else:
        self.metafile: MetaFile = MetaFile(project_dir=project_dir)

        self.account = None
        self._init_account(account, fail_on_error=False)

        if not self.contracts_dir.is_dir():
            raise FileNotFoundError("contracts directory does not exist")

    def get_artifacts(self, force: bool = False) -> AttrDict:
        """ Load the ABI and Bytecode files from the build direcotry and pack them for building the
        Contract objects.

        :param force: Force load, don't just rely on cached dicts.
        """

        # Load only if necessary or forced
        if force is False and len(self._artifacts) > 0:
            return self._artifacts

        # Load the artifacts
        facts = artifacts(project_dir=self.project_dir)
        if not facts:
            # Reset
            self._artifacts = AttrDict()
        else:
            # Convert to dict
            self._artifacts = {x.name: x for x in facts}

        return self._artifacts
    source_contracts = property(get_artifacts)  # TODO: Depreciate
    artifacts = property(get_artifacts)

    @property
    def deployed_contracts(self) -> List[Dict[str, T]]:
        """ The contracts from MetaFile """
        return self.metafile.get_all_contracts()

    def get_contracts(self, force: bool = False):
        """ Instantiate Contract objects to provide to the deploy scripts.

        :param force: Force load, don't just rely on cached data.
        """
        if force is False and len(self._contracts) > 0:
            return self._contracts

        if not self.account:
            self._init_account(fail_on_error=False)

        self._contracts = AttrDict()
        for key in self.artifacts.keys():
            self._contracts[key] = Contract(
                name=key,
                network_name=self.network_name,
                from_account=self.account,
                metafile=self.metafile,
                web3=self.web3,
            )

        return self._contracts
    contracts = property(get_contracts)

    def refresh(self, force: bool = True) -> None:
        """ Return the available kwargs to give to user scripts

        :param force: Don't rely on cache and reload everything.
        :returns: dict of the kwargs to provide to deployer scripts
        """

        self.get_artifacts(force=force)
        self.get_contracts(force=force)
        self.deployed_contracts

    def contracts_to_deploy(self) -> Set[str]:
        """ return a Set of contract names that need deployment """

        self._build_dependency_tree()

        needs_deploy: Set = set()

        """ Iterate through the contracts, see if they need to deploy.  If they do, make sure to
        check the dependency tree to se if others need to be deployed that are linked to it.  This
        way, if a library changes, anything that has it as a dependent will be deployed as well.
        """
        for name, contract in self.contracts.items():
            newest_bytecode = self.artifacts[name].bytecode

            if not newest_bytecode:
                log.warning("Contract {} bytecode artifact not found. This is normal for an "
                            "interface.".format(name))
            else:
                if contract.check_needs_deployment(newest_bytecode):

                    needs_deploy.add(name)

                    assert self.deptree, "Invalid dependency tree. This is probably a bug."

                    el, _ = self.deptree.search_tree(contract.name)

                    if el and el.has_dependencies():
                        needs_deploy.update({x.name for x in el.get_dependencies()})

        log.debug("Contracts that need to be re-deployed: {}".format(needs_deploy))

        return needs_deploy

    def check_needs_deploy(self, name: str = None) -> bool:
        """ Check if any contracts need to be deployed

        :param name: The name of a contract if checking a specific.
        :returns: bool if deployment is required
        """

        if name is not None and not self.source_contracts.get(name):
            raise FileNotFoundError("Unknown contract: {}".format(name))

        # If we don't know about the contract from the metafile, it needs deploy
        if name is not None and not self.contracts.get(name):
            return True
        elif name is not None:
            newest_bytecode = self.artifacts[name].bytecode
            return self.contracts[name].check_needs_deployment(newest_bytecode)

        log.debug("Deployment is not needed")

        return len(self.contracts_to_deploy()) > 0

    def deploy(self) -> bool:
        """ Deploy the contracts with magic lol

        :returns: bool if deployment succeeded. Failed miserably if it didn't.
        """

        if not self.account:
            self._init_account()
            if not self.account:
                raise DeploymentError("No account available.")

        if self.account and self.web3.eth.getBalance(self.account) == 0:
            log.warning("Account has zero balance ({})".format(self.account))

        if self.network_id != (self.web3.net.chainId or self.web3.net.version):
            raise DeploymentError("Connected node is does not match the provided chain ID")

        self._execute_deploy_scripts()
        self.refresh()

        return True

    def _init_account(self, account=None, fail_on_error=True):
        """ Try and figure out what account to use for deployment """

        if account is not None:
            account = self.web3.toChecksumAddress(account)
            self.account = account
            return

        if self.account is not None:
            return

        yml = NetworksYML(project_dir=self.project_dir)

        if yml.use_default_account(self.network_name):

            self.account = self.metafile.get_default_account()

            if self.account is not None:
                return self.account
            elif fail_on_error:
                raise DeploymentError(
                    "Account needs to be set for deployment. No default account found."
                )

            return None

        elif fail_on_error:

            raise AccountError(
                "Use of default account on this network is not allowed and no account was"
                "provided. You may want to set 'use_default_account: true' for this network."
            )

    def _load_user_scripts(self) -> None:
        """ Load the user deploy scripts from deploy folder as python modules and stash 'em away for
        later execution.
        """

        log.debug("Loading user deploy scripts...")

        script_dir = Path(self.deploy_dir)
        if not script_dir.is_dir():
            raise DeploymentError("deploy directory does not appear to be a directory")

        deploy_scripts = list(script_dir.glob('deploy*.py'))

        if len(deploy_scripts) > 0:
            for node in deploy_scripts:

                log.debug("Executing deploy script {}".format(node.name))
                try:
                    mod = SourceFileLoader(node.name[:-3], str(node)).load_module()
                    self._deploy_scripts.append(mod)
                except ModuleNotFoundError as e:
                    if str(e) == "No module named 'deploy'":
                        raise DeploymentError(
                                "Unable to find deploy module.  Missing deploy/__init__.py?"
                            )
                    else:
                        raise e
        else:
            log.warning("No deploy scripts found")

    def _execute_deploy_scripts(self) -> None:
        """ Execute the project's deploy scripts """

        self._load_user_scripts()

        available_kwargs: Dict = self._get_script_kwargs()

        for script in self._deploy_scripts:
            """
            It should be be flexible for users to write their deploy scripts.
            They can pick and choose what kwargs they want to receive.  To handle
            that, we need to inspect the function to see what they want, then
            provide what we can.
            """
            spec = inspect.getfullargspec(script.main)
            script_kwargs = {k: available_kwargs.get(k) for k in spec.args}
            retval = script.main(**script_kwargs)
            # If a deploy script choses to return False, they're signalling a failure
            if retval is False:
                raise DeploymentError("Deploy script did not complete properly!")

    def _get_script_kwargs(self) -> Dict[str, T]:
        """ Return the available kwargs to give to user scripts

        :returns: dict of the kwargs to provide to deployer scripts
        """

        if not self.account:
            self._init_account()
            if not self.account:
                raise DeploymentError("Account not set.")

        return {
            'contracts': self.contracts,
            'web3': self.web3,
            'deployer_account': self.account,
            'network': self.network_name,
        }

    def _build_dependency_tree(self, force: bool = True) -> ContractDependencyTree:
        """ Build a dependency from compiled bin files """

        if not force and isinstance(self.deptree, ContractDependencyTree):
            return self.deptree

        self.deptree = ContractDependencyTree()

        for name, comp in self.get_artifacts().items():

            # Look for this contract
            parent, _ = self.deptree.search_tree(name)
            if parent is None:
                # Add it as a root dep if not found
                parent = self.deptree.root.add_dependent(name)

            # Get the link definitions from the source file
            defs = bytecode_link_defs(comp.bytecode)
            if len(defs) > 0:
                for d_name, _ in defs:
                    parent.add_dependent(d_name)

        return self.deptree
