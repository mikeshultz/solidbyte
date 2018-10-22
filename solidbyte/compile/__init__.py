from .compiler import Compiler

def compile_all():
    """ Compile all contracts in the current project directory """
    cmp = Compiler()
    cmp.compile_all()