""" Run user scripts
"""
import sys
from ..script import run_scripts
from ..common.utils import collapse_oel
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    parser.add_argument('script', metavar="FILE", type=str, nargs='+',
                        help='Script to run')
    return parser


def main(parser_args):
    """ Execute test """

    scripts_plural = 's' if len(parser_args.script) > 1 else ''

    log.info("Running script{} {}".format(
        scripts_plural,
        ', '.join(parser_args.script))
    )

    res = run_scripts(collapse_oel(parser_args.network), parser_args.script)

    if not res:
        log.error("Script{} returned error".format(scripts_plural))
        sys.exit(1)

    log.info("Script{} run successfully".format(scripts_plural))
    sys.exit()
