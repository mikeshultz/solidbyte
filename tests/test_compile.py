""" Test the compiler functionality """
import json
from solidbyte.compile import Compiler
from .utils import TMP_DIR, write_temp_file, get_file_extension, is_hex

CONTRACT_BIN_FILE_1 = "17f8d6292e50616f31b409949cc5ff8e6aafdc087bba4b16f1d71c270c20af1ed839181900360600190a350610c85565b600782810b900b60009081526002602052604090206004015460011115611051576040805160208082526013908201527f6e6f7468696e6720746f207769746864726177000000000000000000000000008183015290513391600785900b917f8d6292e50616f31b409949cc5ff8e6aafdc087bba4b16f1d71c270c20af1ed839181900360600190a350610c85565b600782810b900b600090815260026020526040808220600480820154600a9092015483517f9a3b7f28000000000000000000000000000000000000000000000000000000008152918201929092526024810191909152815183927300000000000000000deadbeef11112345212345692639a3b7f289260448083019392829003018186803b1580156110e257600080fd5b505af41580156110f6573d6000803e3d6000fd5b505050506040513d604081101561110c57600080fd5b50805160209091015190925090506000821161112457fe5b600784810b900b6000908152600260205260409020600a015460011480156111635750600784810b900b60009081526002602052604090206004015482145b806111a85750600784810b900b6000908152600260205260409020600a015460011080156111a85750600784810b900b60009081526002602052604090206004015482105b15156111b057fe5b600784810b900b6000908152600260205260409020600a01805460019190859081106111d85"
CONTRACT_SOURCE_FILE_1 = """pragma solidity ^0.5.2;

contract Test {

    address public owner;

    constructor() public
    {
        owner = msg.sender;
    }

    function getOwner() public view returns (address)
    {
        return owner;
    }

}
"""


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

    assert compiler.version == '0.5.2+commit.1df8f40c.Linux.g++'  # TODO: why?

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
