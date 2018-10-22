""" initialize a basic project structure and meta files
"""
import sys
from os import path, mkdir, getcwd
from ..common.logging import getLogger, parent_logger
from ..templates import BareTemplate, ERC20Template

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    print("adding new args")
    parser.add_argument('-m', action='store_true', default=False,
                        dest='exclude_migration', help='Exclude migration junk')
    parser.add_argument('--dir-mode', type=str, dest='dir_mode',
                        help='Create directories with mode')
    parser.add_argument('--erc20', action='store_true', dest='erc20',
                        help='Create a project template with an ERC20 contract')
    return parser

def main(parser_args):
    """ Execute init """
    pwd = getcwd()

    user_mode = None
    try:
        if parser_args.dir_mode:
            user_mode = int(parser_args.dir_mode, 8)
    except ValueError: pass

    mode = user_mode or 0o755

    if parser_args.erc20:
        try:
            tmpl = ERC20Template(dir_mode=mode)
            tmpl.initialize()
        except FileExistsError as e:
            log.critical(str(e))
            sys.exit(1)
    else:
        try:
            tmpl = BareTemplate(dir_mode=mode)
            tmpl.initialize()
        except FileExistsError as e:
            log.critical(str(e))
            sys.exit(1)
