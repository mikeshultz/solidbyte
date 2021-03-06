from solidbyte.compile.linker import (
    placeholder_from_def,
    contract_from_def,
    bytecode_link_defs,
    replace_placeholders,
    link_library,
)
from solidbyte.common.web3 import remove_0x
from solidbyte.common.exceptions import LinkError
from .const import (
    ADDRESS_1,
    CONTRACT_BIN_FILE_1,
    CONTRACT_PLACEHOLDER_1,
    LIBRARY_NAME_1,
    CONTRACT_DEF_1,
    CONTRACT_BIN_1,
)


def test_placeholder_from_def():
    pholder = placeholder_from_def(CONTRACT_DEF_1)
    assert pholder == CONTRACT_PLACEHOLDER_1

    try:
        placeholder_from_def(' ')
    except LinkError:
        pass


def test_contract_from_def():
    name = contract_from_def(CONTRACT_DEF_1)
    assert name == LIBRARY_NAME_1

    try:
        contract_from_def(' ')
    except LinkError:
        pass


def test_bytecode_link_defs():
    defs = bytecode_link_defs(CONTRACT_DEF_1)
    assert len(defs) == 1
    primary = defs.pop()
    assert primary[0] == LIBRARY_NAME_1
    assert primary[1] == CONTRACT_PLACEHOLDER_1


def test_replace_placeholders():
    replaced = replace_placeholders(CONTRACT_BIN_FILE_1, CONTRACT_PLACEHOLDER_1, ADDRESS_1)
    replaced_no_comments = ''.join([x for x in replaced.split('\n') if not x.startswith('//')])
    # TODO: Expand on this
    assert replaced != CONTRACT_DEF_1
    assert remove_0x(ADDRESS_1) in replaced, replaced
    assert CONTRACT_PLACEHOLDER_1 not in replaced_no_comments


def test_link_library():
    """ Test the full linker """
    linked_bytecode = link_library(CONTRACT_BIN_FILE_1, {
        LIBRARY_NAME_1: ADDRESS_1,
    })
    assert linked_bytecode != CONTRACT_BIN_FILE_1
    assert remove_0x(ADDRESS_1) in linked_bytecode
    assert CONTRACT_PLACEHOLDER_1 not in linked_bytecode

    # Call with incorrect links, it should fail
    try:
        linked_bytecode = link_library(CONTRACT_BIN_FILE_1, {
            'NotALibrary': ADDRESS_1,
        })
        assert False, "link_library should have thrown"
    except LinkError:
        pass

    # Call with links without defs (should not fail)
    linked_bytecode = link_library(CONTRACT_BIN_1, {
        LIBRARY_NAME_1: ADDRESS_1,
    })
    assert linked_bytecode == CONTRACT_BIN_1
