from solidbyte.common.web3 import web3c
from solidbyte.compile import Compiler
from solidbyte.deploy import Deployer
from solidbyte.testing import run_tests
from .const import TMP_DIR, NETWORK_NAME, PYTEST_TEST_1, CONTRACT_VYPER_SOURCE_FILE_1
from .utils import create_mock_project, write_temp_file


def test_testing():
    """ test that testing works, and that the SB fixtures are available and working """

    test_filename = 'test_testing.py'

    # Create a mock project
    workdir = TMP_DIR.joinpath('test-testing')
    testdir = workdir.joinpath('tests')
    contractdir = workdir.joinpath('contracts')
    deploydir = workdir.joinpath('deploy')

    workdir.mkdir(parents=True)
    testdir.mkdir(parents=True)
    contractdir.mkdir(parents=True)
    deploydir.mkdir(parents=True)

    create_mock_project(workdir)

    # Create a test file
    write_temp_file(PYTEST_TEST_1, test_filename, testdir)

    assert testdir.joinpath(test_filename).exists()
    assert testdir.joinpath(test_filename).is_file()

    # Since we're not using the pwd, we need to use this undocumented API (I know...)
    web3c._load_configuration(workdir.joinpath('networks.yml'))
    web3 = web3c.get_web3(NETWORK_NAME)

    # Need to compile and deploy first
    compiler = Compiler(contractdir, workdir)
    compiler.compile_all()
    d = Deployer(NETWORK_NAME, account=web3.eth.accounts[0], project_dir=workdir,
                 contract_dir=contractdir, deploy_dir=deploydir)
    assert d.check_needs_deploy()
    assert d.deploy()

    exitcode = None
    try:
        exitcode = run_tests(
            NETWORK_NAME,
            args=[str(testdir)],
            web3=web3,
            project_dir=workdir,
            contract_dir=contractdir,
            deploy_dir=deploydir,
        )
    except Exception as err:
        assert False, str(err)

    assert exitcode == 0, "Invalid return code: {}".format(exitcode)
