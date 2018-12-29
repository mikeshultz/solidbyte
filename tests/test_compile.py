""" Test the compiler functionality """
import json
from solidbyte.compile import Compiler
from .const import (
    TMP_DIR,
    CONTRACT_SOURCE_FILE_1,
)
from .utils import (
    write_temp_file,
    get_file_extension,
    is_hex,
)


def check_compiler_output(compiled_dir):
    """ Make sure all the expected files were created by the compiler """
    for fil in compiled_dir.iterdir():
        ext = get_file_extension(fil)
        assert ext in ('bin', 'abi'), "Invalid extensions"
        assert fil.name in ('Test.bin', 'Test.abi'), "Invalid filename"
        if ext == 'bin':
            fil_cont = fil.read_text()
            assert is_hex(fil_cont), "binary file is not hex"
        elif ext == 'abi':
            fil_cont = fil.read_text()
            try:
                json.loads(fil_cont)
            except json.decoder.JSONDecodeError:
                assert False, "Invalid JSON in ABI file"


def test_compile():
    """ test a simple compile """
    test_dir = TMP_DIR.joinpath('test_compile')
    contract_file = write_temp_file(CONTRACT_SOURCE_FILE_1, 'Test.sol', test_dir)
    compiler = Compiler(contract_file.parent, test_dir)

    # TODO: why?
    assert compiler.version == '0.5.2+commit.1df8f40c.Linux.g++', ("Unexpected compiler version: "
                                                                   "{}".format(compiler.version))

    compiler.compile(contract_file.name)

    # Make sure the compiler is putting output files in the right location
    compiled_dir = test_dir.joinpath('build', 'Test')
    assert compiled_dir.exists() and compiled_dir.is_dir()

    # Make sure the compiler created the correct files
    for fil in compiled_dir.iterdir():
        ext = get_file_extension(fil)
        assert ext in ('bin', 'abi'), "Invalid extensions"
        assert fil.name in ('Test.bin', 'Test.abi'), "Invalid filename"
        if ext == 'bin':
            fil_cont = fil.read_text()
            assert is_hex(fil_cont), "binary file is not hex"
        elif ext == 'abi':
            fil_cont = fil.read_text()
            try:
                json.loads(fil_cont)
            except json.decoder.JSONDecodeError:
                assert False, "Invalid JSON in ABI file"


def test_compile_all():
    """ test a simple compile """
    test_dir = TMP_DIR.joinpath('test_compile_all')
    contract_file = write_temp_file(CONTRACT_SOURCE_FILE_1, 'Test.sol', test_dir)
    compiler = Compiler(contract_file.parent, test_dir)

    compiler.compile_all()

    # Make sure the compiler is putting output files in the right location
    compiled_dir = test_dir.joinpath('build', 'Test')
    assert compiled_dir.exists() and compiled_dir.is_dir()

    # Make sure the compiler created the correct files
    check_compiler_output(compiled_dir)
