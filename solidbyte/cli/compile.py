""" compile project contracts
"""
from ..compile import compile_all
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    return parser


def main(parser_args):
    """ Execute test """
    log.info("Compiling contracts...")

    compile_all()
