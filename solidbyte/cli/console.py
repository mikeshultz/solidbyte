""" show version information
"""
from ..common import collapse_oel
from ..common.logging import getLogger
from ..console import SolidbyteConsole

log = getLogger(__name__)


def add_parser_arguments(parser):
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    return parser


def main(parser_args):
    """ Open an interactive solidbyte console """

    log.info("Starting interactive console...")

    network_name = collapse_oel(parser_args.network)
    shell = SolidbyteConsole(network_name=network_name)
    shell.interact()
    shell.save_history(shell.histfile)
