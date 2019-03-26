import pytest
from ..compile import compile_all
from ..deploy import Deployer
from ..common.web3 import web3c
from ..common.metafile import MetaFile
from ..common.networks import NetworksYML
from ..common.exceptions import DeploymentValidationError
from ..common.logging import getLogger
from .plugin import SolidbyteTestPlugin

log = getLogger(__name__)


def run_tests(network_name, args=[], web3=None, project_dir=None, account_address=None,
              keystore_dir=None, gas_report_storage=None):
    """ Run all tests on project

    :param network_name: (:code:`str`) - The name of the network as defined in networks.yml.
    :param args: (:code:`list`) - Arguments to provide to pytest
    :param web3: (:class:`web3.Web3`) - The Web3 instance to use
    :param project_dir: (:class:`pathlib.Path`) - The project directory (default: pwd)
    :param account_address: (:code:`str`) - Address of the deployer account
    :param keystore_dir: (:class:`pathlib.Path`) - Path to the keystore. (default:
      :code:`~/.ethereum/keystore`)
    :param gas_report_storage: (:class:`solidbyte.testing.gas.GasReportStorage`) - An instance of
        :code:`GasReportStorage` to use if making a gas report
    """

    yml = NetworksYML(project_dir=project_dir)

    # Use default account if none was specified
    if not account_address:
        mfile = MetaFile(project_dir=project_dir)
        account_address = mfile.get_default_account()
        if not account_address:
            raise DeploymentValidationError("Default account not set and no account provided.")

    log.debug("Using account {} for deployer.".format(account_address))

    log.info("Compiling contracts for testing...")
    compile_all()

    log.info("Checking if deployment is necessary...")

    # First, see if we're allowed to deploy, and whether we need to
    deployer = Deployer(
        network_name=network_name,
        account=account_address,
        project_dir=project_dir,
    )

    if (deployer.check_needs_deploy()
            and yml.network_config_exists(network_name)
            and yml.autodeploy_allowed(network_name)):

        if not account_address:
            raise DeploymentValidationError("Account needs to be provided for autodeployment")

        log.info("Deploying contracts...")

        deployer.deploy()

    elif deployer.check_needs_deploy() and not (
            yml.network_config_exists(network_name)
            and yml.autodeploy_allowed(network_name)):

        raise DeploymentValidationError(
            "Deployment is required for network but autodpeloy is not allowed.  Please deploy "
            "your contracts using the `sb deploy` command."
        )

    if not web3:
        web3 = web3c.get_web3(network_name)

    retval = None
    try:
        retval = pytest.main(args, plugins=[
                SolidbyteTestPlugin(
                    network_name=network_name,
                    web3=web3,
                    project_dir=project_dir,
                    keystore_dir=keystore_dir,
                    gas_report_storage=gas_report_storage,
                )
            ])
    except Exception:
        log.exception("Exception occurred while running tests.")
        return 255

    return retval
