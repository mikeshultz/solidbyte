""" account opperations
"""
from getpass import getpass
from ..accounts import Accounts
from ..common.logging import getLogger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """


    parser.add_argument('-k', '--keystore', type=str,
                        default='~/.ethereum/keystore',
                        help='The Ethereum keystore directory to load accounts from')

    # Subcommands
    subparsers = parser.add_subparsers(title='Account Commands',
                                        dest='account_command',
                                        help='Perform various Ethereum account operations')

    # List accounts
    list_parser = subparsers.add_parser('list', help="List all accounts")
    
    # Create account
    list_parser = subparsers.add_parser('create', help="Create a new account")
    
    # Set default account
    list_parser = subparsers.add_parser('default', help="Set the default account")

    return parser

def main(parser_args):
    """ Execute test """
    log.info("Account operations")

    accts = Accounts(keystore_dir=parser_args.keystore)

    if parser_args.account_command == 'create':
        print("creating account...")
        password = getpass('Encryption password:')
        addr = accts.create_account(password)
        print("Created new account: {}".format(addr))
    else:
        print("Accounts")
        print("========")
        for a in accts.get_accounts():
            print('{} [bal: {}]'.format(a.address, a.balance))