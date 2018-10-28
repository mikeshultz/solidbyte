""" account opperations
"""
from getpass import getpass
from ..accounts import Accounts
from ..common.metafile import MetaFile
from ..common.logging import getLogger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """


    parser.add_argument('-k', '--keystore', type=str,
                        default='~/.ethereum/keystore',
                        help='The Ethereum keystore directory to load accounts from')
    parser.add_argument('-n', '--network', type=str, required=False,
                        help='Ethereum network to connect the console to')

    # Subcommands
    subparsers = parser.add_subparsers(title='Account Commands',
                                        dest='account_command',
                                        help='Perform various Ethereum account operations')

    # List accounts
    list_parser = subparsers.add_parser('list', help="List all accounts")
    
    # Create account
    create_parser = subparsers.add_parser('create', help="Create a new account")
    
    # Set default account
    default_parser = subparsers.add_parser('default', help="Set the default account")
    default_parser.add_argument('-a', '--address', type=str,
                        dest="default_address", required=True,
                        help='The address of the account to set default')

    return parser

def main(parser_args):
    """ Execute test """
    log.info("Account operations")

    accts = Accounts(network_name=parser_args.network,
                        keystore_dir=parser_args.keystore)

    if parser_args.account_command == 'create':
        print("creating account...")
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
        default_string = lambda a: "*" if a.address == default_account else ""
        print("Accounts")
        print("========")
        for a in accts.get_accounts():
            print('{}{} [bal: {}]'.format(
                default_string(a),
                a.address,
                a.balance
                ))