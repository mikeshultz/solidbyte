""" initialize a basic project structure and meta files
"""
import sys
from os import path, mkdir, getcwd
from ..common.logging import getLogger, parent_logger
from ..templates import get_templates, init_template

log = getLogger(__name__)

def add_parser_arguments(parser):
    """ Add additional subcommands onto this command """
    parser.add_argument('-m', action='store_true', default=False,
                        dest='exclude_migration', help='Exclude migration junk')
    parser.add_argument('--dir-mode', type=str, dest='dir_mode',
                        help='Create directories with mode')
    parser.add_argument('-t', '--template', type=str, dest='template',
                        help='Create project structure using template')
    parser.add_argument('-l', '--list-templates', action='store_true', dest='list_templates',
                        help='Show all available templates')
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

    if parser_args.list_templates:
        templates = get_templates()
        print("Available templates")
        print("===================")
        for tmpl in templates:
            print(" - {}".format(tmpl))
    else:
        tmpl = init_template(parser_args.template or 'bare')
        try:
            tmpl.initialize()
        except FileExistsError as e:
            log.critical(str(e))
            sys.exit(1)
