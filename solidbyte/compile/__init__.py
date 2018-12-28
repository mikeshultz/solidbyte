from .compiler import Compiler
from .linker import link_library, clean_bytecode  # noqa: F401


def compile_all():
    """ Compile all contracts in the current project directory """
    cmp = Compiler()
    cmp.compile_all()
