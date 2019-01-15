""" run project tests
"""
import sys
from ..testing import run_tests
from ..common import collapse_oel
from ..common.exceptions import DeploymentValidationError
from ..common import store
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    parser.add_argument('-a', '--address', type=str, required=False,
                        help='Address of the Ethereum account to use for deployment')
    parser.add_argument(
        '-p',
        '--passphrase',
        metavar='PASSPHRASE',
        type=str,
        dest='passphrase',
        help='The passphrase to use to decrypt the account.'
    )
    parser.add_argument('FILE', type=str, nargs='*',
                        help='Explicit test files to run')
    return parser


def main(parser_args):
    """ Execute test """
    log.info("Executing project tests...")

    if parser_args.passphrase:
        # Set this for use later
        store.set(store.Keys.DECRYPT_PASSPHRASE, parser_args.passphrase)

    network_name = collapse_oel(parser_args.network)
    if len(parser_args.FILE) > 0:
        log.debug("Running tests in {}".format(', '.join(parser_args.FILE)))
        args = parser_args.FILE
    else:
        args = list()
    try:
        run_tests(network_name, args=args, account_address=parser_args.address)
    except DeploymentValidationError as err:
        if 'autodeployment' in str(err):
            log.error("The -a/--address option or --default must be provided for autodeployment")
            sys.exit(1)
        else:
            raise err
