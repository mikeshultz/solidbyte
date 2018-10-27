""" show version information
"""
from ..common.logging import getLogger, parent_logger
from ..deploy import Deployer
from ..common.metafile import MetaFile

log = getLogger(__name__)

def add_parser_arguments(parser):
    return parser

def main(parser_args):
    """ Show details about deployments """

    deployer = Deployer()
    source_contracts = deployer.get_source_contracts()
    metafile = MetaFile()
    network_id = 1

    print("Current Deployed Contracts")
    print("==========================")

    for name, c in source_contracts.items():
        addr = 'n/a'
        date = 'n/a'
        deployed_c = metafile.get_contract(c.name)
        if deployed_c \
            and deployed_c.networks.get(network_id) \
            and deployed_c.networks[network_id].get('deployedInstances') \
            and len(deployed_c.networks[network_id]['deployedInstances']) > 0:

            addr = deployed_c.networks[network_id]['deployedInstances'][-1].get('address')
            date = deployed_c.networks[network_id]['deployedInstances'][-1].get('date')

        print("{}: {} ({})".format(name, addr, date))