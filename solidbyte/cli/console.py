""" show version information
"""
from ..common.logging import getLogger, parent_logger
from ..console import SolidbyteConsole

log = getLogger(__name__)

def add_parser_arguments(parser):
    parser.add_argument('-n', '--network', type=str, required=True,
                        help='Ethereum network to connect the console to')
    return parser

def main(parser_args):
    """ Open an interactive solidbyte console """

    log.info("Starting interactive console...")

    shell = SolidbyteConsole(network_name=parser_args.network)
    shell.interact()
    shell.save_history(shell.histfile)