""" These are integration tests running commands as if a user was using solidbyte.  These tests
    are SLOOOOWWWW.  It's been all put into one test because it takes a couple of minutes to setup
    the venv and install Solidbyte.
"""
import os
import pytest
from pathlib import Path
from subprocess import Popen, PIPE
from .const import TMP_DIR, SOLIDBYTE_COMMAND


def no_error(output):
    return (
        b'ERROR' not in output
        and b'CRITICAL' not in output
        and b'Exception' not in output
    )


def execute_command_assert_no_error_success(cmd):
    """ Execute a shell command and assert there's no error and return code shows success """
    assert type(cmd) == list
    list_proc = Popen(cmd, stdout=PIPE)
    list_output = list_proc.stdout.read()
    assert no_error(list_output)
    list_proc.wait()
    assert list_proc.returncode == 0, "Invalid return code from command"


def test_cli_integration(mock_project, virtualenv):
    """ Test valid CLI `accounts` commands """

    orig_pwd = Path.cwd()

    # Our command
    sb = SOLIDBYTE_COMMAND

    with mock_project() as mock:

        TMP_KEY_DIR = TMP_DIR.joinpath('test-keys')

        os.chdir(mock.paths.project)

        # test `sb version`
        execute_command_assert_no_error_success([sb, 'version'])

        # test `sb accounts list`
        execute_command_assert_no_error_success([sb, 'accounts', 'list'])

        # test `sb accounts [network] list`
        execute_command_assert_no_error_success([sb, 'accounts', 'test', 'list'])

        # test `sb accounts create`
        # Need to deal with stdin for the account encryption passphrase
        # execute_command_assert_no_error_success([
        #     sb,
        #     'accounts',
        #     '-k',
        #     str(TMP_KEY_DIR),
        #     'create'
        # ])

        # test `sb accounts default -a [account]`
        # Need an account for this command
        # execute_command_assert_no_error_success([
        #     sb,
        #     'accounts',
        #     'default',
        #     '-k',
        #     str(TMP_KEY_DIR),
        #     '-a',
        #     ACCOUNT
        # ])

        # test `sb compile`
        execute_command_assert_no_error_success([sb, 'compile'])

        # test `sb console [network]`
        # Disabled for now.  It's interactive and no idea how to deal with that
        # execute_command_assert_no_error_success([sb, 'console', 'test'])

        # test `sb deploy [network] -a [account]`
        # Disabled.  Need an account to test with
        # execute_command_assert_no_error_success([
        #     sb,
        #     'deploy',
        #     'test',
        #     '-a',
        #     '0xdeadbeef'
        # ])

        # test `sb show [network]`
        execute_command_assert_no_error_success([sb, 'show', 'test'])

        # test `sb test [network]`
        # TODO: Currently throwing an exception.  Look into it.
        # execute_command_assert_no_error_success([sb, 'test', 'test'])

    # Create a new project without the mock
    project_dir = TMP_DIR.joinpath('test-cli-init')
    project_dir.mkdir()
    os.chdir(project_dir)

    # test `sb init --list-templates`
    execute_command_assert_no_error_success([sb, 'init', '--list-templates'])

    # test `sb init -t [template]`
    execute_command_assert_no_error_success([sb, 'init', '-t', 'erc20'])

    # Head back to where we were
    os.chdir(orig_pwd)
