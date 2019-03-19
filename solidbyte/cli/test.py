""" run project tests
"""
import sys
from pathlib import Path
from tabulate import tabulate
from ..testing import run_tests
from ..compile.artifacts import artifacts
from ..common import collapse_oel
from ..common.exceptions import DeploymentValidationError
from ..common import store
from ..common.web3 import web3c, remove_0x
from ..common.logging import ConsoleStyle, getLogger
from ..testing.gas import GasReportStorage

log = getLogger(__name__)


# TODO: Make these configurable?
GAS_WARN = 1e5
GAS_BAD = 1e6
GAS_ERROR = 47e5  # Ropsten is at 4.7m


def highlight_gas(gas):
    """ Uses console color highlights to indicate high gas usage """

    if gas >= GAS_ERROR:
        return '{}{}{}'.format(
            ConsoleStyle.CRITICAL,
            gas,
            ConsoleStyle.END
        )
    elif gas >= GAS_BAD:
        return '{}{}{}'.format(
            ConsoleStyle.ERROR,
            gas,
            ConsoleStyle.END
        )
    elif gas >= GAS_WARN:
        return '{}{}{}'.format(
            ConsoleStyle.WARNING,
            gas,
            ConsoleStyle.END
        )

    return gas


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('network', metavar="NETWORK", type=str, nargs=1,
                        help='Ethereum network to connect the console to')
    parser.add_argument('-a', '--address', type=str, required=False,
                        help='Address of the Ethereum account to use for deployment')
    parser.add_argument('-g', '--gas', action='store_true', required=False,
                        help='Finish with a gas report')
    parser.add_argument(
        '-p',
        '--passphrase',
        metavar='PASSPHRASE',
        type=str,
        dest='passphrase',
        help='The passphrase to use to decrypt the account.'
    )
    parser.add_argument('FILE', type=str, nargs='*',
                        help='Explicit test files to run')
    return parser


def main(parser_args):
    """ Execute test """
    log.info("Executing project tests...")

    return_code = 0

    if parser_args.passphrase:
        # Set this for use later
        store.set(store.Keys.DECRYPT_PASSPHRASE, parser_args.passphrase)

    network_name = collapse_oel(parser_args.network)
    if len(parser_args.FILE) > 0:
        log.debug("Running tests in {}".format(', '.join(parser_args.FILE)))
        args = parser_args.FILE
    else:
        args = list()

    # If the user set debug, make sure pytest doesn't squash output
    if '-d' in sys.argv:
        args.append('-s')

    web3 = web3c.get_web3(network_name)

    report = None
    if parser_args.gas:
        report = GasReportStorage()

    try:
        return_code = run_tests(network_name, web3=web3, args=args,
                                account_address=parser_args.address,
                                keystore_dir=parser_args.keystore, gas_report_storage=report)
    except DeploymentValidationError as err:
        if 'autodeployment' in str(err):
            log.error("The -a/--address option or --default must be provided for autodeployment")
            sys.exit(1)
        else:
            raise err
    else:
        if return_code != 0:
            log.error("Tests have failed. Return code: {}".format(return_code))
        else:
            if parser_args.gas:

                facts = artifacts(project_dir=Path.cwd())
                sigs_resolver = dict()

                for cc in facts:
                    for item in cc.abi:
                        if item.get('type') in ('function'):
                            inputs = [x.get('type') for x in item.get('inputs')]
                            sig = "{}({})".format(item.get('name'), ','.join(inputs))
                            sig_hash = web3.sha3(text=sig).hex()
                            four_byte = remove_0x(sig_hash)[:8]
                            sigs_resolver[four_byte] = sig

                report.update_gas_used_from_chain(web3)
                report_data = report.get_report()

                report_table = []

                for func in report_data.keys():
                    lo = min(report_data[func])
                    hi = max(report_data[func])
                    avg = round(sum(report_data[func]) / len(report_data[func]))
                    report_table.append([
                        sigs_resolver.get(func, 'Unknown'),
                        highlight_gas(lo),
                        highlight_gas(hi),
                        highlight_gas(avg),
                    ])

                log.debug("Rendering report...")

                print(tabulate(report_table, headers=['Function', 'Low', 'High', 'Avg']))
                print("\nTotal transactions: {}".format(len(report.transactions)))
                if len(report.transactions) > 0:
                    print("Total gas used: {}".format(report.total_gas))
                    print("Average gas per tx: {}".format(round(
                        report.total_gas / len(report.transactions)
                    )))

                log.debug("Report rendering complete.")

        sys.exit(return_code)
