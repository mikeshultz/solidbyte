""" Vyper utilities """
import re
from typing import List
from vyper.parser.parser import parse_to_ast
from ..common.utils import to_path
from ..common.logging import getLogger

log = getLogger(__name__)


# Function def regex, probably gonna be janky
TYPE_BITS = r'(256|128|64|32|16|8|4|2|1)'
VYPER_TYPES = r'(uint{}|int{}|bytes{}|string|address)*'.format(TYPE_BITS, TYPE_BITS, TYPE_BITS)
ARG_SPEC = r'(([\w]+)\:\s*' + VYPER_TYPES + r'(, )*)*'
FUNCTION = r'^(def [\w\_]+\(' + ARG_SPEC + r'\)){1}(\:|[\s]+\-\>[\s]+' + VYPER_TYPES + r'\:){1}'
PASS_BODY = r'([\n\r\s]*(pass)*)*'
FUNC_MODIFYING = r'(\s*(modifying|constant){1}){1}'
BODYLESS_FUNCTION = FUNCTION + FUNC_MODIFYING + PASS_BODY


def source_extract(source_text, start_ln, end_ln):
    source_list = source_text.split('\n')
    if end_ln < 0:
        end_ln = len(source_list)
    return '\n'.join([source_list[i] for i in range(start_ln, end_ln)])


def vyper_funcs_from_source(source_text):
    """ Pull function defs from an AST """

    source_ast: List = parse_to_ast(source_text)

    funcs: List = []

    for i in range(0, len(source_ast)):
        node = source_ast[i]
        start = node.lineno
        end = -1

        if i < len(source_ast) - 1:
            end = source_ast[i+1].lineno - 1

        funcs.append(source_extract(source_text, start, end))

    return funcs


def is_bodyless_func(func_text):
    """ Identify if a code block is a bodyless/interface function """
    return re.match(BODYLESS_FUNCTION, func_text) is not None


def is_vyper_interface(source_text: str):
    """ Identify if the provided source text is a vyper interface """

    funcs = vyper_funcs_from_source(source_text)

    if len(funcs) < 1:
        return False

    return any([is_bodyless_func(func) for func in funcs])


def dirs_in_dir(searchpath):
    searchpath = to_path(searchpath)
    assert searchpath.is_dir(), "Non-directory given to dirs_in_dir()"
    found_dirs = []
    for node in searchpath.iterdir():
        if node.is_dir():
            found_dirs.append(node)
    return found_dirs


def vyper_import_to_file_paths(workdir, importpath):
    """ Get the possible import paths for an interface import """

    log.debug("Looking for vyper import {}".format(importpath))

    workdir = to_path(workdir)
    import_parts = str(importpath).split('.')
    resolved_path = workdir.joinpath(
        '/'.join(import_parts) + '.vy',
    )

    log.debug("Import resolved to {}".format(resolved_path))

    if not resolved_path.is_file():
        return None
    return resolved_path
