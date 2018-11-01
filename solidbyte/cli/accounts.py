""" account opperations
"""
from getpass import getpass
from ..accounts import Accounts
from ..common import collapse_oel
from ..common.web3 import web3c
from ..common.metafile import MetaFile
from ..common.logging import getLogger

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """


    parser.add_argument('-k', '--keystore', type=str,
                        default='~/.ethereum/keystore',
                        help='The Ethereum keystore directory to load accounts from')
    parser.add_argument('network', metavar="NETWORK", type=str, nargs="?",
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

    network_name = collapse_oel(parser_args.network)
    web3 = web3c.get_web3(network_name)
    accts = Accounts(network_name=network_name,
                        keystore_dir=parser_args.keystore, web3=web3)

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