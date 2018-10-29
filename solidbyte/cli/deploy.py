""" deploy contracts where necessary
"""
import sys
from ..compile import compile_all
from ..deploy import Deployer
from ..common.logging import getLogger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('-n', '--network', type=str, required=True,
                        help='Ethereum network to deploy contracts to')
    parser.add_argument('-a', '--address', type=str, required=True,
                        help='Address of the Ethereum account to use for deployment')
    #parser.add_argument('-c', '--contract', action='store_true', default=False,
    #                    help='Deploy only specified contract')
    #parser.add_argument('-f', '--force', action='store_true', default=False,
    #                    help='Force deployment(not recommended)')
    return parser

def main(parser_args):
    """ Deploy contracts """
    log.info("Deploying contracts...")

    deployer = Deployer(network_name=parser_args.network, account=parser_args.address)
    compile_all()
    deployer.refresh() # TODO: Necessary?

    # Make sure we actually need to deploy
    if not deployer.check_needs_deploy():
        log.info("No changes, deployment unnecessary")
        sys.exit()

    deployer.deploy()

    contracts = deployer.contracts

    log.info("Contracts fully deployed!")
    log.info("--------------------------------------")
    for name in deployer.contracts.keys():
        contract = deployer.contracts[name]
        log.info("{}: {}".format(contract.name, contract.address))
    log.info("--------------------------------------")