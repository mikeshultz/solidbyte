""" show version information
"""
from ..common.logging import getLogger, parent_logger
from ..console import SolidbyteConsole

log = getLogger(__name__)

def add_parser_arguments(parser):
    return parser

def main(parser_args):
    """ Open an interactive solidbyte console """

    log.info("Starting interactive console...")

    shell = SolidbyteConsole()
    shell.interact()
    shell.save_history(shell.histfile)