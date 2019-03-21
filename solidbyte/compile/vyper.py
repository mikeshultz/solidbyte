""" Compiler utilities """
import re
from typing import List
from vyper.parser.parser import parse_to_ast


# BODYLESS_FUNCTION = r'(def [\w]+\(\)\:)[\s]+(constant|modifying)'
# Function def regex, probably gonna be janky
TYPE_BITS = r'(1|2|4|8|16|32|64|128|256)'
VYPER_TYPES = r'(uint{}|int{})*'.format(TYPE_BITS, TYPE_BITS)
FUNCTION = r'^(def [\w\_]+\(\)){1}(\:| \-> (' + VYPER_TYPES + r')*\:)'
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

    for func in funcs:
        if is_bodyless_func(func):
            return True

    return False
