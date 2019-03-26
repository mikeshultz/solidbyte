""" The initial CLI command router """

import sys
import argparse
from pathlib import Path
from importlib import import_module
from ..common import store
from ..common.logging import getLogger, loggingShutdown

log = getLogger(__name__)

MODULES = [
    'init',
    'test',
    'compile',
    'deploy',
    'version',
    'show',
    'console',
    'accounts',
    # 'install',
    'metafile',
    'sigs',
    'script',
]

IMPORTED_MODULES = {}
DEFAULT_KEYSTORE = '~/.ethereum/keystore'


def parse_args(argv=None):
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(description='SolidByte Ethereum development tools')
    parser.add_argument('-d', action='store_true',
                        help='Print debug level messages')
    parser.add_argument('-k', '--keystore', type=str, dest="keystore",
                        default=DEFAULT_KEYSTORE,
                        help='Ethereum account keystore directory to use.')

    subparsers = parser.add_subparsers(title='Submcommands', dest='command',
                                       help='do the needful')

    """
    Each module must implement the following minimum API:
        - add_parser_arguments(parser) - A function that takes an argparse
            parser and adds the arguments it wants for its command
            implementation.
        - main(parser_args) - The primary function to run that provides
            parser_args as a kwarg
    """
    for mod in MODULES:
        IMPORTED_MODULES[mod] = import_module('solidbyte.cli.{}'.format(mod))
        module_subparser = subparsers.add_parser(mod, help=IMPORTED_MODULES[mod].__doc__)
        module_subparser = IMPORTED_MODULES[mod].add_parser_arguments(module_subparser)

    # Help command
    subparsers.add_parser('help', help='print usage')

    return parser.parse_args(argv), parser


def main(argv=None):

    args, parser = parse_args(argv)

    if not hasattr(args, 'command') or not args.command:
        log.warning('noop')
        sys.exit(1)

    if args.command == 'help':
        parser.print_help()
        sys.exit(0)

    if args.command not in MODULES:
        log.error('Unknown command: {}'.format(args.command))
        sys.exit(2)

    if args.keystore != DEFAULT_KEYSTORE:
        log.info("Using keystore at {}".format(args.keystore))
        store.set(store.Keys.KEYSTORE_DIR, args.keystore)

    # Set some session data we'll need throughout
    store.set(store.Keys.PROJECT_DIR, Path.cwd())

    IMPORTED_MODULES[args.command].main(parser_args=args)

    loggingShutdown()
    sys.exit(0)
