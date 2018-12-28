""" Functions used for linking libraries in contracts

Example placeholder: __$13811623e8434e588b8942cf9304d14b96$__
"""
import re
from typing import List
from ..common import all_defs_in, defs_not_in
from ..common.web3 import remove_0x
from ..common.exceptions import LinkError
from ..common.logging import getLogger

log = getLogger(__name__)

# Regexes to match parts of a solc bin file
# TODO: Always 34?
LINK_CONTRACT_REGEX = r':([A-Za-z0-9]+)$'
LINK_PLACEHOLDER_REGEX = r'\$[A-Za-z0-9]{34}\$'
#BYTECODE_PLACEHOLDER_REGEX = r'__(\$[A-Za-z0-9]{34}\$)__'
BYTECODE_PLACEHOLDER_REGEX = '__({})__'


def make_placeholder_regex(placeholder: str) -> str:
    """ Return a regex pattern for a placeholder """
    placeholder = re.escape(placeholder)
    return re.compile(BYTECODE_PLACEHOLDER_REGEX.format(placeholder))


def placeholder_from_def(s: str) -> str:
    """ return a placeholder form a solc file link definition """
    placeholder = re.search(LINK_PLACEHOLDER_REGEX, s)
    if not placeholder:
        raise LinkError("Unable to find placeholder")
    try:
        return placeholder.group(0)
    except IndexError:
        raise LinkError("Could not get placeholder from def")


def contract_from_def(s: str) -> str:
    """ return a contract name form a solc file link definition """
    contract_match = re.search(LINK_CONTRACT_REGEX, s)
    if not contract_match:
        raise LinkError("Unable to find contract")
    return contract_match.group(1)


def bytecode_link_defs(bytecode) -> List[tuple]:
    link_defs = []
    bytecode_list = bytecode.split('\n')
    for ln in bytecode_list:
        if ln.startswith('// '):
            contract_name = contract_from_def(ln)
            placeholder = placeholder_from_def(ln)
            if contract_name and placeholder:
                link_defs.append((contract_name, placeholder))
            else:
                log.warn("Possible link definition missing or extra comment in bytecode "
                         "file: {}".format(ln))
    return link_defs


def replace_placeholders(bytecode: str, placeholder: str, addr: str) -> str:
    """ Replace the placeholders with the contract address """
    pattern = make_placeholder_regex(placeholder)
    return re.sub(pattern, remove_0x(addr), bytecode)


def clean_bytecode(bytecode: str) -> str:
    """ Clean the bytecode string of any comments and whitespace """
    blist = [x for x in bytecode.split('\n') if x.strip() != '' and not x.startswith('//')]
    return ''.join(blist)


def link_library(bytecode: str, links: dict) -> str:
    if len(links) < 1:
        return bytecode

    defs = bytecode_link_defs(bytecode)
    if not all_defs_in(defs, links):
        missing_defs = defs_not_in(defs, links)
        raise LinkError("Not all libraries can be linked. Missing link addresses for: {}".format(
            missing_defs
        ))

    linked_bytecode = ''
    if len(defs) > 0:
        for mos in defs:
            linked_bytecode = replace_placeholders(bytecode, mos[1], links[mos[0]])
    else:
        linked_bytecode = bytecode

    return clean_bytecode(linked_bytecode)