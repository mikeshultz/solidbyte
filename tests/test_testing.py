from solidbyte.common.web3 import web3c
from solidbyte.compile import Compiler
from solidbyte.deploy import Deployer
from solidbyte.testing import run_tests
from .const import NETWORK_NAME


def test_testing(mock_project):
    """ test that testing works, and that the SB fixtures are available and working """

    with mock_project() as mock:

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        # Need to compile and deploy first
        compiler = Compiler(mock.paths.contracts, mock.paths.project)
        compiler.compile_all()
        d = Deployer(NETWORK_NAME, account=web3.eth.accounts[0], project_dir=mock.paths.project,
                     contract_dir=mock.paths.contracts, deploy_dir=mock.paths.deploy)
        assert d.check_needs_deploy()
        assert d.deploy()

        exitcode = None
        try:
            exitcode = run_tests(
                NETWORK_NAME,
                args=[str(mock.paths.tests)],
                web3=web3,
                project_dir=mock.paths.project,
                contract_dir=mock.paths.contracts,
                deploy_dir=mock.paths.deploy,
            )
        except Exception as err:
            assert False, str(err)

        assert exitcode == 0, "Invalid return code: {}".format(exitcode)


def test_testing_autodeploy(mock_project):
    """ test that testing works with automatic deployment """

    with mock_project() as mock:

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        exitcode = None
        try:
            exitcode = run_tests(
                NETWORK_NAME,
                args=[str(mock.paths.tests)],
                web3=web3,
                project_dir=mock.paths.project,
                contract_dir=mock.paths.contracts,
                deploy_dir=mock.paths.deploy,
            )
        except Exception as err:
            assert False, str(err)

        assert exitcode == 0, "Invalid return code: {}".format(exitcode)
