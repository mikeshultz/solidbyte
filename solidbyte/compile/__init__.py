from .compiler import Compiler
from .linker import (  # noqa: F401
    link_library,
    clean_bytecode,
    bytecode_link_defs,
)


def compile_all():
    """ Compile all contracts in the current project directory """
    cmp = Compiler()
    cmp.compile_all()
