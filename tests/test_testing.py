from solidbyte.common.web3 import web3c
from solidbyte.compile import Compiler
from solidbyte.deploy import Deployer
from solidbyte.testing import run_tests
from .const import NETWORK_NAME


def test_testing(mock_project):
    """ test that testing works, and that the SB fixtures are available and working """

    with mock_project() as mock:

        # Create a mock project
        testdir = mock.joinpath('tests')
        contractdir = mock.joinpath('contracts')
        deploydir = mock.joinpath('deploy')

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.joinpath('networks.yml'))
        web3 = web3c.get_web3(NETWORK_NAME)

        # Need to compile and deploy first
        compiler = Compiler(contractdir, mock)
        compiler.compile_all()
        d = Deployer(NETWORK_NAME, account=web3.eth.accounts[0], project_dir=mock,
                     contract_dir=contractdir, deploy_dir=deploydir)
        assert d.check_needs_deploy()
        assert d.deploy()

        exitcode = None
        try:
            exitcode = run_tests(
                NETWORK_NAME,
                args=[str(testdir)],
                web3=web3,
                project_dir=mock,
                contract_dir=contractdir,
                deploy_dir=deploydir,
            )
        except Exception as err:
            assert False, str(err)

        assert exitcode == 0, "Invalid return code: {}".format(exitcode)
