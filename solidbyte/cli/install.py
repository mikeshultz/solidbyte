""" install a package from ethPM
"""
import sys
from ..ethpm import EthPM
from ..common import collapse_oel
from ..common.web3 import web3c
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    parser.add_argument('package', metavar="PACKAGE", type=str, nargs=1,
                        help='The EthPM package to install')
    return parser


def main(parser_args):
    """ Execute test """
    log.info("Executing project tests...")

    network_name = collapse_oel(parser_args.network)
    web3 = web3c.get_web3(network_name)
    epm = EthPM(web3)
    success = epm.install(collapse_oel(parser_args.package))

    if not success:
        log.error("Install of {} failed".format(parser_args.package))
        sys.exit(0)
