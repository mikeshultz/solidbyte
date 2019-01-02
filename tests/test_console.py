import pytest
from solidbyte.console import (
    get_default_banner,
    SolidbyteConsole,
)
from .const import NETWORK_ID, CONSOLE_TEST_ASSERT_LOCALS


def test_get_default_banner():
    """ Super useful test!  Way to shoot for coverage! """
    banner = get_default_banner(NETWORK_ID)
    assert type(banner) == str
    assert str(NETWORK_ID) in banner


def test_console(mock_project):
    """ Test the interactive console """

    with mock_project():
        sc = SolidbyteConsole()
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
                    assert str(err) == '0', "Invalid exit code"
