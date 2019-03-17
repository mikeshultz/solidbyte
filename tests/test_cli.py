""" These are integration tests running commands as if a user was using solidbyte.  These tests
    are SLOOOOWWWW.  It's been all put into one test because it takes a couple of minutes to setup
    the venv and install Solidbyte.
"""
import os
import re
import time
import pytest
from pathlib import Path
from subprocess import Popen, PIPE
from .const import NETWORK_NAME, TMP_DIR, PASSWORD_1, SOLIDBYTE_COMMAND, CONSOLE_TEST_ASSERT_LOCALS

ACCOUNT_MATCH_PATTERN = r'^(0x[A-Fa-f0-9]{40})'


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
    assert no_error(list_output), list_output
    list_proc.wait()
    assert list_proc.returncode == 0, "Invalid return code from command"
    return list_output


def execute_command_assert_error(cmd):
    """ Test that a command errors with a return code > 0 """
    assert type(cmd) == list
    proc = Popen(cmd)
    proc.wait()
    assert proc.returncode > 0, "Invalid return code from command"


def test_cli_integration(mock_project, ganache):
    """ Test valid CLI `accounts` commands """

    orig_pwd = Path.cwd()

    # Our command
    sb = SOLIDBYTE_COMMAND

    with mock_project():
        with ganache() as gopts:

            TMP_KEY_DIR = TMP_DIR.joinpath('test-keys')

            # test `sb version`
            execute_command_assert_no_error_success([sb, 'version'])

            # test `sb help`
            execute_command_assert_no_error_success([sb, 'help'])

            # test `sb accounts create`
            # Need to deal with stdin for the account encryption passphrase
            execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                'accounts',
                'create',
                '-p',
                PASSWORD_1,
            ])

            # test `sb accounts list`
            # execute_command_assert_no_error_success([sb, 'accounts', 'list'])

            # test `sb accounts [network] list`
            accounts_output = execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                'accounts',
                gopts.network_name,
                'list',
            ]).decode('utf-8')

            # We're going to need the default account later
            default_account = None
            print("accounts_output: {}".format(accounts_output))
            for ln in accounts_output.split('\n'):
                # 0xC4cf518bDeDe4bdbE3d98f2F8E3195c7d9DC080B
                print("### matching {} against {}".format(ACCOUNT_MATCH_PATTERN, ln))
                match = re.match(ACCOUNT_MATCH_PATTERN, ln)
                if match:
                    default_account = match.group(1)
                    break
            assert default_account is not None, "Did not find an account to use"

            # test `sb accounts default -a [account]`
            execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                'accounts',
                'default',
                '-a',
                default_account
            ])

            # test `sb compile`
            execute_command_assert_no_error_success([sb, 'compile'])

            # test `sb console [network]`
            # Disabled for now.  It's interactive and no idea how to deal with that
            # execute_command_assert_no_error_success([sb, 'console', 'test'])

            # test `sb deploy [network] -a [account]`
            # Disabled.  Need an account to test with
            execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                'deploy',
                gopts.network_name,
                '-a',
                default_account,
                '-p',
                PASSWORD_1,
            ])

            # test `sb show [network]`
            execute_command_assert_no_error_success([sb, 'show', gopts.network_name])

            # test `sb test [network]`
            # TODO: Currently throwing an exception.  Look into it.
            execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                '-d',
                'test',
                '-g',
                '-p',
                PASSWORD_1,
                gopts.network_name,
            ])

            # test `sb metafile backup metafile.json.bak`
            execute_command_assert_no_error_success([sb, 'metafile', 'backup', 'metafile.json.bak'])

            # test `sb metafile cleanup --dry-run`
            execute_command_assert_no_error_success([sb, 'metafile', 'cleanup', '--dry-run'])

            # test `sb metafile cleanup`
            execute_command_assert_no_error_success([sb, 'metafile', 'cleanup'])

            # test `sb metafile cleanup` when there's nothing to cleanup
            execute_command_assert_no_error_success([sb, 'metafile', 'cleanup'])

            # test `sb deploy -a ADDRESS NETWORK`
            execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                'deploy',
                '-a',
                default_account,
                '-p',
                PASSWORD_1,
                gopts.network_name,
            ])

            # test `sb script NETWORK FILE`
            # TODO: There's currently no persistance between the deploy command and the following
            #       commands.  Might need to use ganache to test with instead of eth_tester.
            execute_command_assert_no_error_success([
                sb,
                'script',
                gopts.network_name,
                'scripts/test_success.py',
            ])

            # test `sb sigs`
            execute_command_assert_no_error_success([sb, 'sigs'])

            # test `sb sigs [contract]`
            execute_command_assert_no_error_success([sb, 'sigs', 'Test'])

            # Create a new project without the mock
            project_dir = TMP_DIR.joinpath('test-cli-init')
            project_dir.mkdir()
            os.chdir(project_dir)

            # test `sb init --list-templates`
            execute_command_assert_no_error_success([sb, 'init', '--list-templates'])

            # test `sb init -t [template]`
            execute_command_assert_no_error_success([sb, 'init', '-t', 'erc20'])

            execute_command_assert_no_error_success([sb, 'compile'])
            execute_command_assert_no_error_success([
                sb,
                '-k',
                str(TMP_KEY_DIR),
                'test',
                NETWORK_NAME,
                '-a',
                default_account,
                '-p',
                PASSWORD_1
            ])

            # Create a new project without the mock
            project_dir2 = TMP_DIR.joinpath('test-cli-init2')
            project_dir2.mkdir()
            os.chdir(project_dir2)

            # test `sb init -t [template]`
            execute_command_assert_no_error_success([sb, '-d', 'init', '--dir-mode', '750'])

            stat = project_dir2.joinpath('contracts').stat()
            assert stat.st_mode == 0o750 + 0o40000  # 0o40000 means 'directory'

    os.chdir(orig_pwd)


def test_cli_invalid(mock_project, ganache):
    """ Test valid CLI `accounts` commands """

    # Our command
    sb = SOLIDBYTE_COMMAND

    with mock_project():

        # test `sb` (noop)
        execute_command_assert_error([sb])

        # Test a command that doesn't exist
        execute_command_assert_error([sb, 'notacommand'])

        # Test init with an invalid template
        execute_command_assert_error([sb, 'init', '-t', 'notatemplate'])

        # Test `sb metafile` without the needed subcommand
        execute_command_assert_error([sb, 'metafile'])


@pytest.mark.skip("Test does not work")
def test_cli_console(mock_project):
    """ test the interactive console and some present commands """

    with mock_project():
        # Run the console command
        console_proc = Popen([SOLIDBYTE_COMMAND, 'console', 'test'], universal_newlines=True,
                             bufsize=1, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)

        time.sleep(3)  # Arbitrary number that may fail randomly on loaded machines...
        # Pretend we're a user by typing randomly in the console
        commands = CONSOLE_TEST_ASSERT_LOCALS.copy()
        seen_output = False
        while True:
            out = console_proc.stdout.readline()
            err = console_proc.stderr.readline()

            if seen_output:
                cmd = commands.pop(0)
                console_proc.stdin.write(cmd)
                console_proc.stdin.flush()

            # We're waiting for the console to make the first move
            if (out or err) and not seen_output:
                seen_output = True

            if commands and len(commands) == 0:
                break

            time.sleep(0.5)

        console_proc.stdin.close()
        out = console_proc.stdout.read()
        err = console_proc.stderr.read()
        console_proc.stdout.close()
        console_proc.stderr.close()
        assert False
