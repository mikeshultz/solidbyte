""" show version information
"""
from tabulate import tabulate
from ..common.logging import getLogger
from ..deploy import Deployer
from ..common import collapse_oel
from ..common.metafile import MetaFile
from ..common.web3 import web3c

log = getLogger(__name__)


def add_parser_arguments(parser):
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    return parser


def main(parser_args):
    """ Show details about deployments """

    network_name = collapse_oel(parser_args.network)
    deployer = Deployer(network_name=network_name)
    # TODO: Show all networks?
    web3 = web3c.get_web3(network_name)
    network_id = web3.net.chainId or web3.net.version
    source_contracts = deployer.get_artifacts()
    metafile = MetaFile()

    print("Current Deployed Contracts")
    print("==========================")

    table_out = []

    for name, c in source_contracts.items():
        addr = 'n/a'
        date = 'n/a'
        deployed_c = metafile.get_contract(c.name)
        if deployed_c \
                and deployed_c.get('networks') \
                and deployed_c['networks'].get(network_id) \
                and deployed_c['networks'][network_id].get('deployedInstances') \
                and len(deployed_c['networks'][network_id]['deployedInstances']) > 0:

            addr = deployed_c['networks'][network_id]['deployedInstances'][-1].get('address')
            date = deployed_c['networks'][network_id]['deployedInstances'][-1].get('date')
            table_out.append([name, addr, date])

    print(tabulate(table_out, headers=['Contract', 'Address', 'Date Deployed']))
