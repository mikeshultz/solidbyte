""" run project tests
"""
from ..testing import run_tests
from ..common import collapse_oel
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    return parser


def main(parser_args):
    """ Execute test """
    log.info("Executing project tests...")

    network_name = collapse_oel(parser_args.network)
    run_tests(network_name=network_name)
