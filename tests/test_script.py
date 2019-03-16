""" Tests for script command """
from solidbyte.common.web3 import web3c
from solidbyte.deploy import Deployer
from solidbyte.compile.compiler import Compiler
from solidbyte.script import get_contracts, run_script, run_scripts
from .const import (
    NETWORK_NAME,
)


def test_get_contracts(mock_project):
    """ Test that get_contracts() returns proper Web3 contract objects """
    with mock_project() as mock:

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        deployer_account = web3.eth.accounts[0]

        # Init the Deployer
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )
        d.deploy()

        contracts = get_contracts(NETWORK_NAME)
        assert len(contracts) > 0, "No contracts found"

        # Make sure it has all the expected Web3 Contract props
        assert hasattr(contracts['Test'], 'functions')
        assert hasattr(contracts['Test'], 'address')
        assert hasattr(contracts['Test'], 'abi')


def test_script(mock_project):
    """ test user  script running """

    with mock_project() as mock:
        test_script = mock.paths.scripts.joinpath('test_success.py')
        assert test_script.is_file()

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        deployer_account = web3.eth.accounts[0]

        # Init the Deployer
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )
        d.deploy()

        assert run_script(NETWORK_NAME, str(test_script)), "Script unexpectedly failed"
        assert run_scripts(NETWORK_NAME, [str(test_script)]), "Scripts unexpectedly failed"


def test_script_failure(mock_project):
    """ test that scripts fail properly """

    with mock_project() as mock:
        test_script = mock.paths.scripts.joinpath('test_fail.py')
        assert test_script.is_file()

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        deployer_account = web3.eth.accounts[0]

        # Init the Deployer
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )
        d.deploy()

        assert run_script(NETWORK_NAME, str(test_script)) is False, "Script unexpectedly succeeded"
        assert run_scripts(NETWORK_NAME, [str(test_script)]) is False, (
            "Scripts unexpectedly succeeded"
        )
