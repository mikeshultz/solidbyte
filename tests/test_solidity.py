""" Tests for vyper integration.
"""
import json
from solidbyte.compile import Compiler
from .const import (
    CONTRACT_SOLIDITY_IMPLEMENTER_NAME,
    CONTRACT_SOLIDITY_INTERFACE_NAME,
    CONTRACT_SOLIDITY_IMPLEMENTER,
    CONTRACT_SOLIDITY_INTERFACE,
)
from .utils import (
    write_temp_file,
    get_file_extension,
    is_hex,
)


def test_compile_solidity_with_interface(temp_dir):
    """ test a simple compile """
    with temp_dir() as test_dir:
        contract_dir = test_dir.joinpath('contracts')
        print("CONTRACTTTTTTTTTTTTTTTTTT: ", CONTRACT_SOLIDITY_IMPLEMENTER)
        contract_file = write_temp_file(
            CONTRACT_SOLIDITY_IMPLEMENTER,
            '{}.sol'.format(CONTRACT_SOLIDITY_IMPLEMENTER_NAME),
            contract_dir
        )
        write_temp_file(
            CONTRACT_SOLIDITY_INTERFACE,
            '{}.sol'.format(CONTRACT_SOLIDITY_INTERFACE_NAME),
            contract_dir
        )

        compiler = Compiler(test_dir)
        compiler.compile(contract_file.name)

        # Make sure the compiler is putting output files in the right location
        compiled_dir = test_dir.joinpath('build', CONTRACT_SOLIDITY_IMPLEMENTER_NAME)
        assert compiled_dir.exists() and compiled_dir.is_dir()

        # Make sure the compiler created the correct files
        for fil in compiled_dir.iterdir():

            ext = get_file_extension(fil)

            assert ext in ('bin', 'abi'), "Invalid extensions"
            assert fil.name in (
                '{}.bin'.format(CONTRACT_SOLIDITY_IMPLEMENTER_NAME),
                '{}.abi'.format(CONTRACT_SOLIDITY_IMPLEMENTER_NAME),
                '{}.bin'.format(CONTRACT_SOLIDITY_INTERFACE_NAME),
                '{}.abi'.format(CONTRACT_SOLIDITY_INTERFACE_NAME),
            ), (
                "Invalid filename"
            )

            if ext == 'bin':

                # Interface won't have binary
                if CONTRACT_SOLIDITY_IMPLEMENTER_NAME in fil.name:

                    fil_cont = fil.read_text()
                    assert is_hex(fil_cont), "binary file is not hex"

            elif ext == 'abi':

                fil_cont = fil.read_text()

                try:
                    json.loads(fil_cont)
                except json.decoder.JSONDecodeError:
                    assert False, "Invalid JSON in ABI file"
