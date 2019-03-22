""" Tests for vyper integration.
"""
import json
from solidbyte.compile import Compiler
from .const import (
    CONTRACT_VYPER_SOURCE_FILE_2,
    CONTRACT_VYPER_INTERFACE_FILE_2,
    EXPECTED_VYPER_VERSION,
)
from .utils import (
    write_temp_file,
    get_file_extension,
    is_hex,
)


def test_compile_vyper_with_interface(temp_dir):
    """ test a simple compile """
    with temp_dir() as test_dir:
        contract_dir = test_dir.joinpath('contracts')
        contract_file = write_temp_file(CONTRACT_VYPER_SOURCE_FILE_2, 'TestVyper.vy', contract_dir)
        write_temp_file(
            CONTRACT_VYPER_INTERFACE_FILE_2,
            'ITestInterface.vy',
            contract_dir
        )
        compiler = Compiler(test_dir)

        # If this changes, this test should be reevaluated
        assert compiler.vyper_version == EXPECTED_VYPER_VERSION, (
            "Unexpected compiler version: {}".format(compiler.vyper_version)
        )

        compiler.compile(contract_file.name)

        # Make sure the compiler is putting output files in the right location
        compiled_dir = test_dir.joinpath('build', 'TestVyper')
        assert compiled_dir.exists() and compiled_dir.is_dir()

        # Make sure the compiler created the correct files
        for fil in compiled_dir.iterdir():
            ext = get_file_extension(fil)
            assert ext in ('bin', 'abi'), "Invalid extensions"
            assert fil.name in ('TestVyper.bin', 'TestVyper.abi'), "Invalid filename"
            if ext == 'bin':
                fil_cont = fil.read_text()
                assert is_hex(fil_cont), "binary file is not hex"
            elif ext == 'abi':
                fil_cont = fil.read_text()
                try:
                    json.loads(fil_cont)
                except json.decoder.JSONDecodeError:
                    assert False, "Invalid JSON in ABI file"
