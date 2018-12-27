""" show version information
"""
import solidbyte
import web3
from ..compile import Compiler
from ..common.logging import getLogger

log = getLogger(__name__)


def add_parser_arguments(parser):
    return parser


def main(parser_args):
    """ Execute test """
    log.debug("web3.__version__: {}".format(web3.__version__))

    compiler = Compiler()

    print("solidbyte: {}".format(solidbyte.__version__))
    print("solc: {}".format(compiler.version))
    print("web3.py: {}".format(web3.__version__))
