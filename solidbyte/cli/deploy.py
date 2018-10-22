""" compile project contracts
"""
from ..deploy import Contracts
from ..common.logging import getLogger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    #parser.add_argument('-d', action='store_true', default=False,
    #                    help='debug level output')
    return parser

def main(parser_args):
    """ Deploy contracts """
    log.info("Deploying contracts...")

    contracts = Contracts()
    contracts.deploy_all()