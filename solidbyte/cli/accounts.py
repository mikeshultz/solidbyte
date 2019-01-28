""" account opperations
"""
import sys
from getpass import getpass
from ..accounts import Accounts
from ..common.web3 import web3c
from ..common.metafile import MetaFile
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """

    parser.add_argument('network', metavar="NETWORK", type=str, nargs="?",
                        help='Ethereum network to connect the console to')

    """ This is some hinky shit with a specific version of Python (3.7.0a4+) which was seen on
        Travis, which seems like it will not always be a problem in 3.7.

        See: https://bugs.python.org/issue33109

        Basically, for a brief period of time, the required keyword defaulted to True.  Which makes
        the command `sb accounts` fail, because there's no followup sucommand like:
        `sb accounts list`.  So, we have to play around here and dance because 3.6 does not accept
        the required kwarg.
    """
    subparsers_kwargs = {
        'title': 'Account Commands',
        'dest': 'account_command',
        'help': 'Perform various Ethereum account operations',
    }

    if sys.version_info[0] == 3 and sys.version_info[1] == 7:
        subparsers_kwargs['required'] = False

    subparsers = parser.add_subparsers(**subparsers_kwargs)

    # List accounts
    list_parser = subparsers.add_parser('list', help="List all accounts")  # noqa: F841

    # Create account
    create_parser = subparsers.add_parser('create', help="Create a new account")  # noqa: F841
    create_parser.add_argument(
        '-p',
        '--passphrase',
        metavar='PASSPHRASE',
        type=str,
        nargs="?",
        dest='passphrase',
        help='The passphrase to use to encrypt the keyfile. Leave empty for prompt.'
    )

    # Set default account
    default_parser = subparsers.add_parser('default', help="Set the default account")
    default_parser.add_argument('-a', '--address', type=str,
                                dest="default_address", required=True,
                                help='The address of the account to set default')

    return parser


def main(parser_args):
    """ Execute test """

    if parser_args.network:
        network_name = parser_args.network
    else:
        network_name = None
    web3 = web3c.get_web3(network_name)
    accts = Accounts(network_name=network_name,
                     keystore_dir=parser_args.keystore, web3=web3)

    if parser_args.account_command == 'create':
        print("creating account...")
        if parser_args.passphrase:
            password = parser_args.passphrase
        else:
            password = getpass('Encryption password:')
        addr = accts.create_account(password)
        print("Created new account: {}".format(addr))
    elif parser_args.account_command == 'default':
        print("Setting default account to: {}".format(parser_args.default_address))

        metafile = MetaFile()
        metafile.set_default_account(parser_args.default_address)
    else:
        metafile = MetaFile()
        default_account = metafile.get_default_account()
        default_string = lambda a: "*" if a.address == default_account else ""  # noqa: E731
        print("Accounts")
        print("========")
        for a in accts.get_accounts():
            print('{}{} [bal: {}]'.format(
                    default_string(a),
                    a.address,
                    a.balance
                ))
