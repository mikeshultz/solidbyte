""" Functionality for running user scripts """
import inspect
from types import ModuleType
from typing import Optional, List
from attrdict import AttrDict
# from importlib import SourceFileLoader
# from importlib.abc import SourceLoader
from importlib.util import spec_from_file_location, module_from_spec
from ..deploy import Deployer
from ..common.utils import to_path
from ..common.web3 import web3c
from ..common.exceptions import InvalidScriptError
from ..common.logging import getLogger

log = getLogger(__name__)
deployer: Optional[Deployer] = None


def get_contracts(network):
    """ Get a list of web3 contract instances. """
    global deployer

    if not deployer:
        deployer = Deployer(network_name=network)

    contracts = AttrDict({})

    for contract_name, contract in deployer.contracts.items():
        try:
            # TODO: Internal API?  Better option?
            contracts[contract_name] = contract._get_web3_contract()
        except AssertionError:
            log.warning("Unable to get a deployed instance for contract {}".format(contract_name))

    return contracts


def get_availble_script_kwargs(network):
    global deployer

    if not deployer:
        deployer = Deployer(network_name=network)

    contracts = get_contracts(network)

    return {
        'web3': web3c.get_web3(network),
        'contracts': contracts,
        'deployer_account': deployer.account,
        'network': network,
    }


def run_script(network: str, script: str) -> bool:
    """ Runs a user script """

    scriptPath = to_path(script)
    script_kwargs = get_availble_script_kwargs(network)

    spec = spec_from_file_location(scriptPath.name[:-3], str(scriptPath))
    mod: Optional[ModuleType] = module_from_spec(spec)

    # try:
    #     log.debug("Loading deploy script {}".format(scriptPath))
    #     mod = SourceFileLoader(scriptPath.name[:-3], str(scriptPath)).exec_module()
    # except ModuleNotFoundError as e:
    #     if str(e) == "No module named 'deploy'":
    #         raise ScriptError(
    #                 "Unable to import script."
    #             )
    #     else:
    #         raise e

    if not spec or not spec.loader or not mod:
        raise InvalidScriptError("Script not found")

    spec.loader.exec_module(mod)

    if not hasattr(mod, 'main'):
        print("MOD", dir(mod))
        raise InvalidScriptError("Function main() must be defined in script")

    func_spec = inspect.getfullargspec(mod.main)
    script_kwargs = {k: script_kwargs.get(k) for k in func_spec.args}
    retval = mod.main(**script_kwargs)

    # If a script choses to return False, they're signalling a failure
    if retval is False:
        log.error("Script has indicated an error!")
        return False

    return True


def run_scripts(network: str, scripts: List[str]) -> bool:
    """ Run multiple user scripts """

    if len(scripts) < 1:
        log.warning("No scripts provided")
        return True

    return all([run_script(network, script) for script in scripts])
