import pytest
from solidbyte.cli.handler import parse_args
from .const import ADDRESS_1


def test_argparse_help():
    argv = 'help'.split()
    args, _ = parse_args(argv)
    assert args.command == 'help'


@pytest.mark.parametrize('argv,expected', [
    ('accounts', [
        ('command', 'accounts'),
        ('account_command', None),
        ('network', None),
    ]),
    ('accounts list', [
        ('command', 'accounts'),
        ('account_command', 'list'),
        ('network', None),
    ]),
    ('accounts test list', [
        ('command', 'accounts'),
        ('account_command', 'list'),
        ('network', 'test'),
    ]),
    ('accounts create', [
        ('command', 'accounts'),
        ('account_command', 'create'),
    ]),
    ('accounts default -a {}'.format(ADDRESS_1), [
        ('command', 'accounts'),
        ('account_command', 'default'),
        ('default_address', ADDRESS_1),
    ]),
    ('compile', [
        ('command', 'compile'),
    ]),
    ('console test', [
        ('command', 'console'),
        ('network', ['test']),  # TODO: Weirdness with argparse and nargs=1?
    ]),
    ('deploy test -a {}'.format(ADDRESS_1), [
        ('command', 'deploy'),
        ('network', ['test']),  # TODO: Weirdness with argparse and nargs=1?
    ]),
    ('init', [
        ('command', 'init'),
        ('dir_mode', None),
        ('template', None),
        ('list_templates', False),
    ]),
    ('init -t erc20', [
        ('command', 'init'),
        ('dir_mode', None),
        ('template', 'erc20'),
        ('list_templates', False),
    ]),
    ('init -l', [
        ('command', 'init'),
        ('dir_mode', None),
        ('template', None),
        ('list_templates', True),
    ]),
    ('init --list-templates', [
        ('command', 'init'),
        ('dir_mode', None),
        ('template', None),
        ('list_templates', True),
    ]),
    ('init --dir-mode 755', [
        ('command', 'init'),
        ('dir_mode', '755'),
        ('template', None),
        ('list_templates', False),
    ]),
    ('install test mypackage', [
        ('command', 'install'),
        ('network', ['test']),  # TODO: Weirdness with argparse and nargs=1?
        ('package', ['mypackage']),  # TODO: Weirdness with argparse and nargs=1?
    ]),
    ('show test', [
        ('command', 'show'),
        ('network', ['test']),  # TODO: Weirdness with argparse and nargs=1?
    ]),
    ('test test', [
        ('command', 'test'),
        ('network', ['test']),  # TODO: Weirdness with argparse and nargs=1?
    ]),
    ('version', [
        ('command', 'version'),
    ]),
])
def test_argparse_valid(argv, expected):
    """ Test command parsing """

    args, _ = parse_args(argv.split())
    for expect in expected:
        assert hasattr(args, expect[0])
        if expect[1] is None:
            assert not getattr(args, expect[0])
        else:
            assert getattr(args, expect[0]) == expect[1]


@pytest.mark.parametrize('argv', [
    'accounts default',
    'compile path/to/myfile.sol',  # TODO: This maybe should be implemented
    'console',
    'deploy',
    'deploy test',
    'install',
    'install mypackage',  # TODO: This maybe should be implemented
    'show',
    'test',
])
def test_argparse_invalid(argv):
    """ Test invalid command parsing. Argparse will SystemExit when it sees invalid commands.

        Honestly, not really sure why these are being tested.  This may be bad UX.  Consider if
        there's a better way of dealing with these commands that are likely to be expected by a
        user.  But right now, we want these to fail.  So make sure they fail.
    """

    try:
        args, _ = parse_args(argv.split())
        assert False, "This command should have caused an exit"
    except SystemExit:
        assert True
