""" show version information
"""
from pathlib import Path
from tabulate import tabulate
from ..compile.artifacts import artifacts, contract_artifacts
from ..common.web3 import web3c
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):

    parser.add_argument('contract_name', metavar="CONTRACT_NAME", type=str, nargs="?",
                        help='Contract name to get signatures for')

    return parser


def main(parser_args):
    """ Show details about deployments """

    web3 = web3c.get_web3()
    if parser_args.contract_name:
        single = contract_artifacts(project_dir=Path.cwd(), name=parser_args.contract_name)
        facts = {single}
    else:
        facts = artifacts(project_dir=Path.cwd())

    print("Contract Function and Event Signatures")
    print("======================================")

    for cc in facts:
        if len(cc.abi) > 0:
            print("\n\n==========================")
            print("= {}".format(cc.name))
            print("==========================\n")
            table_output = []
            for item in cc.abi:
                if item.get('type') in ('function', 'event'):
                    inputs = [x.get('type') for x in item.get('inputs')]
                    sig = "{}({})".format(item.get('name'), ','.join(inputs))
                    sig_hash = web3.sha3(text=sig).hex()
                    table_output.append([sig, sig_hash[2:10], sig_hash])
            print(tabulate(table_output, headers=['Signature', '4-byte', 'Full Signature']))
