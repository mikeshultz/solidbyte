""" run project tests
"""
from ..testing import run_tests
from ..common.logging import getLogger, parent_logger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    #parser.add_argument('-d', action='store_true', default=False,
    #                    help='debug level output')
    return parser

def main(parser_args):
    """ Execute test """
    log.info("Executing project tests...")

    run_tests()