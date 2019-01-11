""" deploy contracts where necessary
"""
import sys
from ..compile import compile_all
from ..deploy import Deployer
from ..common import store, collapse_oel
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    parser.add_argument('-a', '--address', type=str, required=True,
                        help='Address of the Ethereum account to use for deployment')
    parser.add_argument(
        '-p',
        '--passphrase',
        metavar='PASSPHRASE',
        type=str,
        nargs="?",
        dest='passphrase',
        help='The passphrase to use to encrypt the keyfile. Leave empty for prompt.'
    )
    # parser.add_argument('-c', '--contract', action='store_true', default=False,
    #                     help='Deploy only specified contract')
    # parser.add_argument('-f', '--force', action='store_true', default=False,
    #                     help='Force deployment(not recommended)')
    return parser


def main(parser_args):
    """ Deploy contracts """
    log.info("Deploying contracts...")

    if parser_args.passphrase:
        # Set this for use later
        store.set(store.Keys.DECRYPT_PASSPHRASE, parser_args.passphrase)

    network_name = collapse_oel(parser_args.network)
    deployer = Deployer(network_name=network_name, account=parser_args.address)
    compile_all()
    deployer.refresh()  # TODO: Necessary?

    # Make sure we actually need to deploy
    if not deployer.check_needs_deploy():
        log.info("No changes, deployment unnecessary")
        sys.exit()

    deployer.deploy()

    log.info("Contracts fully deployed!")
    log.info("--------------------------------------")
    for name in deployer.contracts.keys():
        contract = deployer.contracts[name]
        log.info("{}: {}".format(contract.name, contract.address))
    log.info("--------------------------------------")
