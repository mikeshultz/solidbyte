""" run project tests
"""
from ..testing import run_tests
from ..common.logging import getLogger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('-n', '--network', type=str, required=True, 
                        default='test',
                        help='Ethereum network to connect the console to')
    return parser

def main(parser_args):
    """ Execute test """
    log.info("Executing project tests...")

    run_tests(network_name=parser_args.network)