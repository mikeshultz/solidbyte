from solidbyte.common.web3 import web3c
from solidbyte.compile import Compiler
from solidbyte.deploy import Deployer
from solidbyte.console import (
    get_default_banner,
    SolidbyteConsole,
)
from .const import (
    NETWORK_ID,
    NETWORK_NAME,
    CONSOLE_TEST_ASSERT_LOCALS,
    CONSOLE_TEST_ASSERT_CONTRACTS,
)


def test_get_default_banner():
    """ Super useful test!  Way to shoot for coverage! """
    banner = get_default_banner(NETWORK_ID)
    assert type(banner) == str
    assert str(NETWORK_ID) in banner


def test_console(mock_project):
    """ Test the interactive console """

    with mock_project() as mock:

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        assert mock.paths.project.joinpath('networks.yml').exists()
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        sc = SolidbyteConsole(network_name=NETWORK_NAME, web3=web3)
        commands = CONSOLE_TEST_ASSERT_LOCALS.copy()
        while len(commands) > 0:
            cmd = commands.pop(0)
            if 'exit' not in cmd:
                assert not sc.push(cmd.rstrip('\n'))  # Should return false if success
            else:
                try:
                    sc.push(cmd.rstrip('\n'))
                    assert False, "Should have exited"
                except SystemExit as err:
                    """ Since AssertionError exits with code 0 for some reason, our test exits
                        cleanly with code 1337.
                    """
                    assert str(err) != b'1337', "Invalid exit code: {}".format(str(err))


def test_console_contracts(mock_project):
    """ Test that the interactive console picks up deployed contracts """

    with mock_project() as mock:

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        assert mock.paths.project.joinpath('networks.yml').exists()
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        # Compile the contracts for deployment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Deploy contracts
        deployer_account = web3.eth.accounts[0]
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )
        assert d.deploy()

        sc = SolidbyteConsole(network_name=NETWORK_NAME, web3=web3)
        commands = CONSOLE_TEST_ASSERT_CONTRACTS.copy()
        while len(commands) > 0:
            cmd = commands.pop(0)
            if 'exit' not in cmd:
                assert not sc.push(cmd.rstrip('\n'))  # Should return false if success
            else:
                try:
                    sc.push(cmd.rstrip('\n'))
                    assert False, "Should have exited"
                except SystemExit as err:
                    """ Since AssertionError exits with code 0 for some reason, our test exits
                        cleanly with code 1337.
                    """
                    assert str(err) != b'1337', "Invalid exit code: {}".format(str(err))
