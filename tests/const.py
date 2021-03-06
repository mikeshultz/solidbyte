# flake8: noqa
from pathlib import Path
from datetime import datetime
from hexbytes import HexBytes

# Filesystem
TMP_DIR = Path('/tmp/solidbyte-test-{}'.format(datetime.now().timestamp()))

SOLIDBYTE_COMMAND = 'sb'
SOLIDBYTE_MODULE = 'solidbyte'

EXPECTED_VYPER_VERSION = '0.2.4'

# Ethereum stuff
NETWORK_ID = 999
NETWORK_NAME = 'test'
TEST_HASH = '0x9c22ff5f21f0b81b113e63f7db6da94fedef11b2119b4088b89664fb9a3cb658'
PASSWORD_1 = 'asdf1234'
ADDRESS_1 = '0x2c21CE1CEe5B9B1C8aa71ab09A47a5361A36BEaD'
ADDRESS_2 = '0x2c21CE1cEe5B9b1C8aA71aB09a47a5361a36beAE'
ADDRESS_2_HASH = '0x4ff6eacd66bd565ddc5e1d660414a8f15d2bb42314b9fc2019dadbf29eefa07a'
ADDRESS_2_NOT_CHECKSUM = '0x2c21ce1cEe5B9B1C8aA71aB09a47a5361a36beAE'
NETWORK_ID = 999
GANACHE_PORT = 8576  # Testing port, not to conflict with standard
GANACHE_NETWORK_NAME = 'testganache'
ABI_OBJ_1 = [{
  "inputs": [],
  "payable": False,
  "stateMutability": "nonpayable",
  "type": "constructor"
}]
BYTECODE_HASH_1 = '0x6385b18cc3f884baad806ee4508837d3a27c734268f9555f76cd12ec3ff38339'
OBVIOUS_RETURN_CODE = 254
TX_INPUT = '0x4ff6eacd66bd565ddc5e1d660414a8f15d2bb42314b9fc2019dadbf29eefa07a'
TX_FUNC_SIG = '4ff6eacd'

FUNC_SIG = 'myFunction(uint256 myParam,int128 myOtherParam)'
FUNC_SIG_HASH = '0x15a3c1f7c6e6eae7296debf117d144d83fb458baeace5c4fb8647bfa683234b8'

DUMB_CONTRACT_ABI = [{'constant': False, 'inputs': [{'name': 'value', 'type': 'uint256'}], 'name': 'emitUint256', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'value', 'type': 'address'}], 'name': 'emitAddress', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'val', 'type': 'address'}], 'name': 'AddressEvent', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'val', 'type': 'uint256'}], 'name': 'Uint256Event', 'type': 'event'}]
EVENT_SIG = 'AddressEvent(address)'
EVENT_SIG_HASH = HexBytes('0xa0786e1009edc9cbf8898c0299c4518c0d18ec943fa88b2af645b4dd024d7a49')
EVENT_ABI = {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'val', 'type': 'address'}], 'name': 'AddressEvent', 'type': 'event'}
EVENT_RECEIPT = {'transactionHash': HexBytes('0xd2e7370fb4a519449c89506c5baefe30a000e723d728e0f5e14d2c752950875e'), 'transactionIndex': 0, 'blockHash': HexBytes('0x3c2257289c1f883affa4fdd9b52231d00226666e1d432e15cc0b554cfa0ef329'), 'blockNumber': 5, 'from': '0x717dd920e935b5078fc67717713b2a62987a8044', 'to': '0x25820e39ceb1a46fbd332bebc0ec53c3fb5033c7', 'gasUsed': 23942, 'cumulativeGasUsed': 23942, 'contractAddress': None, 'logs': [{'logIndex': 0, 'transactionIndex': 0, 'transactionHash': HexBytes('0xd2e7370fb4a519449c89506c5baefe30a000e723d728e0f5e14d2c752950875e'), 'blockHash': HexBytes('0x3c2257289c1f883affa4fdd9b52231d00226666e1d432e15cc0b554cfa0ef329'), 'blockNumber': 5, 'address': '0x25820e39CEB1A46FBd332BebC0eC53c3fB5033c7', 'data': '0x000000000000000000000000717dd920e935b5078fc67717713b2a62987a8044', 'topics': [HexBytes('0xa0786e1009edc9cbf8898c0299c4518c0d18ec943fa88b2af645b4dd024d7a49')], 'type': 'mined'}], 'status': 1, 'logsBloom': HexBytes('0x00000000000000004000000000000000000000000004000080000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000080010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'), 'v': '0x1c', 'r': '0x6d093c5d47fe6377cececc34fc0e915c56b6b792a1abc4b50153e122c3c9e870', 's': '0x653e07276d3af113b57e12097afef4006b7f96da80e713b65ab92885977be1a7'}

CONTRACT_NAME_1 = "MyContract"
LIBRARY_NAME_1 = "MyLibrary"
CONTRACT_PLACEHOLDER_1 = "$13811623e8434e588b8942cf9304d14b96$"
CONTRACT_BIN_FILE_1 = """17f8d6292e50616f31b409949cc5ff8e6aafdc087bba4b16f1d71c270c20af1ed839181900360600190a350610c85565b600782810b900b60009081526002602052604090206004015460011115611051576040805160208082526013908201527f6e6f7468696e6720746f207769746864726177000000000000000000000000008183015290513391600785900b917f8d6292e50616f31b409949cc5ff8e6aafdc087bba4b16f1d71c270c20af1ed839181900360600190a350610c85565b600782810b900b600090815260026020526040808220600480820154600a9092015483517f9a3b7f280000000000000000000000000000000000000000000000000000000081529182019290925260248101919091528151839273__$13811623e8434e588b8942cf9304d14b96$__92639a3b7f289260448083019392829003018186803b1580156110e257600080fd5b505af41580156110f6573d6000803e3d6000fd5b505050506040513d604081101561110c57600080fd5b50805160209091015190925090506000821161112457fe5b600784810b900b6000908152600260205260409020600a015460011480156111635750600784810b900b60009081526002602052604090206004015482145b806111a85750600784810b900b6000908152600260205260409020600a015460011080156111a85750600784810b900b60009081526002602052604090206004015482105b15156111b057fe5b600784810b900b6000908152600260205260409020600a01805460019190859081106111d85

// {} -> /path/to/contracts/{}.sol:{}""".format(CONTRACT_PLACEHOLDER_1, LIBRARY_NAME_1,
                                                LIBRARY_NAME_1)
CONTRACT_DEF_1 = "// {} -> /path/to/contracts/{}.sol:{}".format(CONTRACT_PLACEHOLDER_1,
                                                                LIBRARY_NAME_1, LIBRARY_NAME_1)

CONTRACT_BIN_1 = '608060405234801561001057600080fd5b5060008054600160a060020a0319163317905560ec806100316000396000f3fe6080604052348015600f57600080fd5b5060043610604e577c01000000000000000000000000000000000000000000000000000000006000350463893d20e8811460535780638da5cb5b146082575b600080fd5b60596088565b6040805173ffffffffffffffffffffffffffffffffffffffff9092168252519081900360200190f35b605960a4565b60005473ffffffffffffffffffffffffffffffffffffffff1690565b60005473ffffffffffffffffffffffffffffffffffffffff168156fea165627a7a723058203cf0749d63a9746d388baf77b6f7eca08acd9b74d9ce88825280bc528ba560a80029'  # noqa: E501
CONTRACT_SOURCE_FILE_1 = """pragma solidity ^0.5.2;

contract Test {

    address public owner;
    uint public testVar;

    constructor() public
    {
        owner = msg.sender;
        testVar = 0;
    }

    function getOwner() public view returns (address)
    {
        return owner;
    }

    function setTestVar(uint newValue) public
    {
        testVar = newValue;
    }

}
"""

CONTRACT_VYPER_SOURCE_FILE_1 = """owner: public(address)

@external
def __init__():
    self.owner = msg.sender

@view
@external
def getOwner() -> address:
    return self.owner
"""
CONTRACT_DEPLOY_SCRIPT_1 = """
def main(contracts, deployer_account, web3, network):
    assert contracts is not None
    assert deployer_account is not None
    assert web3 is not None
    assert network is not None

    deployer_balance = web3.eth.getBalance(deployer_account)
    print("BALANCE: {}: {}".format(deployer_account, deployer_balance))

    # If this is the test network, make sure our deployment account is funded
    if deployer_balance == 0 and web3.eth.accounts[0] != deployer_account:
        tx = web3.eth.sendTransaction({
            'from': web3.eth.accounts[0],  # The pre-funded account in ganace-cli
            'to': deployer_account,
            'value': int(1e18),
            'gasPrice': int(3e9),
            })
        receipt = web3.eth.waitForTransactionReceipt(tx)
        assert receipt.status == 1

    print("BALANCE: {}: {}".format(deployer_account, deployer_balance))
    print("id(contracts) == {}".format(id(contracts)))

    Test = contracts.get('Test')
    test = Test.deployed()
    assert test.functions.getOwner().call() is not None
    return True
"""
CONTRACT_VYPER_SOURCE_FILE_2 = """
import ITestInterface as ITestInterface

implements: ITestInterface

counter: uint256

@external
def add_one():
    self.counter += 1

@view
@external
def get_one() -> uint256:
    return self.counter
"""
CONTRACT_VYPER_INTERFACE_FILE_2 = """
@external
def add_one():
    pass

@view
@external
def get_one() -> uint256:
    pass
"""
NETWORKS_YML_1 = """# networks.yml
---
test:
  type: eth_tester
  autodeploy_allowed: true
  use_default_account: true

dev:
  type: auto
  autodeploy_allowed: true
  use_default_account: true

{}:
  type: http
  url: http://localhost:{}/

nodeploy:
  type: eth_tester

""".format(GANACHE_NETWORK_NAME, GANACHE_PORT)
NETWORKS_YML_2 = """# networks.yml
---
test:
  type: eth_tester
  autodeploy_allowed: true
  use_default_account: true

dev:
  type: auto
  autodeploy_allowed: true

geth:
  type: ipc
  file: ~/.ethereum/geth.ipc

infura-mainnet:
  type: websocket
  url: wss://mainnet.infura.io/ws

infura-mainnet-http:
  type: http
  url: https://mainnet.infura.io/asdfkey
"""
NETWORKS_YML_NOCONFIG = """# networks.yml
---
"""
NETWORKS_YML_INVALID_TYPE = """# networks.yml
---
test:
    type: notatype
    file: /tmp/nothing.yml
"""
PYTEST_TEST_1 = """
def test_fixtures(web3, contracts, local_accounts, std_tx):
    assert web3 is not None
    assert contracts is not None
    assert contracts.get('Test') is not None
    assert local_accounts is not None
    # Test that web3 works
    tx_hash = web3.eth.sendTransaction({
        'from': web3.eth.accounts[0],
        'to': web3.eth.accounts[1],
        'value': int(1e18),
        'gasPrice': int(3e9),
        'gas': 21000
    })
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    assert receipt.status == 1
    # Test a contract call
    test = contracts.get('Test')
    tx_hash = test.functions.setTestVar(3).transact(std_tx({
        'from': web3.eth.accounts[0],
        'gas': int(1e5),
    }))
    receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    assert receipt.status == 1
"""

# Console test commands
CONSOLE_TEST_ASSERT_LOCALS = [
    "import sys\n",
    "assert 'web3' in locals(), 'web3 missing'\n",
    "assert 'accounts' in locals(), 'accounts missing'\n",
    "assert 'network' in locals(), 'network missing'\n",
    "assert 'network_id' in locals(), 'network_id missing'\n",
    "assert 'nothing' not in locals(), 'nothing found'\n",
    "sys.exit({})\n".format(OBVIOUS_RETURN_CODE),
]

CONSOLE_TEST_ASSERT_CONTRACTS = [
    "import sys\n",
    "assert 'Test' in locals(), 'Test contract missing'\n",
    "sys.exit({})\n".format(OBVIOUS_RETURN_CODE),
]

####
# Source files for a test project with a library
####

LIBRARY_SOURCE_FILE_1 = """pragma solidity >=0.4.24 <0.6.0;

/**
 * @title SafeMath
 * @dev Math operations with safety checks that revert on error
 */
library SafeMath {
    int256 constant private INT256_MIN = -2**255;

    /**
    * @dev Multiplies two unsigned integers, reverts on overflow.
    */
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
        // benefit is lost if 'b' is also tested.
        // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
        if (a == 0) {
            return 0;
        }

        uint256 c = a * b;
        require(c / a == b);

        return c;
    }

    /**
    * @dev Multiplies two signed integers, reverts on overflow.
    */
    function mul(int256 a, int256 b) internal pure returns (int256) {
        // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
        // benefit is lost if 'b' is also tested.
        // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
        if (a == 0) {
            return 0;
        }

        require(!(a == -1 && b == INT256_MIN)); // This is the only case of overflow not detected by the check below

        int256 c = a * b;
        require(c / a == b);

        return c;
    }

    /**
    * @dev Integer division of two unsigned integers truncating the quotient, reverts on division by zero.
    */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0);
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    }

    /**
    * @dev Integer division of two signed integers truncating the quotient, reverts on division by zero.
    */
    function div(int256 a, int256 b) internal pure returns (int256) {
        require(b != 0); // Solidity only automatically asserts when dividing by 0
        require(!(b == -1 && a == INT256_MIN)); // This is the only case of overflow

        int256 c = a / b;

        return c;
    }

    /**
    * @dev Subtracts two unsigned integers, reverts on overflow (i.e. if subtrahend is greater than minuend).
    */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a);
        uint256 c = a - b;

        return c;
    }

    /**
    * @dev Subtracts two signed integers, reverts on overflow.
    */
    function sub(int256 a, int256 b) internal pure returns (int256) {
        int256 c = a - b;
        require((b >= 0 && c <= a) || (b < 0 && c > a));

        return c;
    }

    /**
    * @dev Adds two unsigned integers, reverts on overflow.
    */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a);

        return c;
    }

    /**
    * @dev Adds two signed integers, reverts on overflow.
    */
    function add(int256 a, int256 b) internal pure returns (int256) {
        int256 c = a + b;
        require((b >= 0 && c >= a) || (b < 0 && c < a));

        return c;
    }

    /**
    * @dev Divides two unsigned integers and returns the remainder (unsigned integer modulo),
    * reverts when dividing by zero.
    */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b != 0);
        return a % b;
    }
}
"""

LIBRARY_SOURCE_FILE_2 = """pragma solidity >=0.4.24 <0.6.0;

/**
 * @title SafeMath
 * @dev Math operations with safety checks that revert on error
 */
library SafeMath {
    int256 constant private INT256_MIN = -2**255;

    /**
    * @dev Multiplies two unsigned integers, reverts on overflow.
    */
    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
        // benefit is lost if 'b' is also tested.
        // See: https://github.com/OpenZeppelin/openzeppelin-solidity/pull/522
        if (a == 0) {
            return 0;
        }

        uint256 c = a * b;
        require(c / a == b);

        return c;
    }

    /**
    * @dev Integer division of two unsigned integers truncating the quotient, reverts on division by zero.
    */
    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        // Solidity only automatically asserts when dividing by 0
        require(b > 0);
        uint256 c = a / b;
        // assert(a == b * c + a % b); // There is no case in which this doesn't hold

        return c;
    }

    /**
    * @dev Subtracts two unsigned integers, reverts on overflow (i.e. if subtrahend is greater than minuend).
    */
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a);
        uint256 c = a - b;

        return c;
    }

    /**
    * @dev Adds two unsigned integers, reverts on overflow.
    */
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a);

        return c;
    }

    /**
    * @dev Divides two unsigned integers and returns the remainder (unsigned integer modulo),
    * reverts when dividing by zero.
    */
    function mod(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b != 0);
        return a % b;
    }
}
"""


LIBRARY_ABI_OBJ_4 = [{'constant': True, 'inputs': [{'name': 'a', 'type': 'uint256'}, {'name': 'b', 'type': 'uint256'}], 'name': 'add', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'pure', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'a', 'type': 'uint256'}, {'name': 'b', 'type': 'uint256'}], 'name': 'sub', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'pure', 'type': 'function'}]
LIBRARY_BYTECODE_4 = '60e561002f600b82828239805160001a6073146000811461001f57610021565bfe5b5030600052607381538281f3fe73000000000000000000000000000000000000000030146080604052600436106059577c01000000000000000000000000000000000000000000000000000000006000350463771602f78114605e578063b67d77c5146090575b600080fd5b607e60048036036040811015607257600080fd5b508035906020013560b0565b60408051918252519081900360200190f35b607e6004803603604081101560a457600080fd5b508035906020013560b4565b0190565b90039056fea165627a7a723058208515cf61bfb0a23f4d03d3655765f880af2644ed78a065c7e8f55fa8b2b4f8030029'
LIBRARY_SOURCE_FILE_3 = """pragma solidity ^0.5.2;

library Unnecessary {
    function add(uint a, uint b) public pure returns (uint)
    {
        return a + b;
    }
    function sub(uint a, uint b) public pure returns (uint)
    {
        return a - b;
    }
}
"""

LIBRARY_SOURCE_FILE_4 = """pragma solidity ^0.5.2;

library Unnecessary {
    function add(uint a, uint b) public pure returns (uint)
    {
        return a + b;
    }

    function sub(uint a, uint b) public pure returns (uint)
    {
        return a - b;
    }

    function mod(uint a, uint b) public pure returns (uint)
    {
        return a % b;
    }
}
"""

CONTRACT_SOURCE_FILE_2 = """pragma solidity ^0.5.2;

import './SafeMath.sol';
import './Unnecessary.sol';

contract TestMath {
    using SafeMath for uint;

    address public owner;

    constructor() public
    {
        owner = msg.sender;
    }

    function getOwner() public view returns (address)
    {
        return owner;
    }

    function div(uint a, uint b) public pure returns (uint)
    {
      return a.div(b);
    }

    function mul(uint a, uint b) public pure returns (uint)
    {
      return a.mul(b);
    }

    function add(uint a, uint b) public pure returns (uint)
    {
      return Unnecessary.add(a, b);
    }

    function sub(uint a, uint b) public pure returns (uint)
    {
      return Unnecessary.sub(a, b);
    }

}
"""

CONTRACT_DEPLOY_SCRIPT_2 = """
def main(contracts, deployer_account, web3, network):
    assert contracts is not None
    assert deployer_account is not None
    assert web3 is not None
    assert network is not None

    deployer_balance = web3.eth.getBalance(deployer_account)

    # If this is the test network, make sure our deployment account is funded
    if deployer_balance == 0:
        tx = web3.eth.sendTransaction({
            'from': web3.eth.accounts[0],  # The pre-funded account in ganace-cli
            'to': deployer_account,
            'value': int(1e18),
            'gasPrice': int(3e9),
            })
        receipt = web3.eth.waitForTransactionReceipt(tx)
        assert receipt.status == 1

    Unnecessary = contracts.get('Unnecessary')
    TestMath = contracts.get('TestMath')
    SafeMath = contracts.get('SafeMath')

    unnecessary = Unnecessary.deployed()
    safeMath = SafeMath.deployed()
    test = TestMath.deployed(links={
      'SafeMath': safeMath.address,
      'Unnecessary': unnecessary.address,
    })
    print("test.functions: {}".format(test.functions))
    assert hasattr(test.functions, 'getOwner')
    assert hasattr(test.functions, 'mul')
    assert hasattr(test.functions, 'div')
    assert hasattr(test.functions, 'add')
    assert hasattr(test.functions, 'sub')
    assert test.functions.getOwner().call() == deployer_account
    assert test.functions.mul(3, 2).call() == 6
    assert test.functions.div(6, 3).call() == 2
    assert test.functions.add(6, 3).call() == 9
    assert test.functions.sub(6, 3).call() == 3
    return True
"""

CONTRACT_SOLIDITY_INTERFACE_NAME = "ITest"
CONTRACT_SOLIDITY_IMPLEMENTER_NAME = "Implementer"
CONTRACT_SOLIDITY_IMPLEMENTER = """pragma solidity ^0.5.2;

import './{}.sol';

contract {} is {} {{
    uint256 public count;

    function addOne(uint256 val) external
    {{
        count += val;
    }}

    function getCount() external view returns (uint256)
    {{
        return count;
    }}
}}
""".format(
    CONTRACT_SOLIDITY_INTERFACE_NAME,
    CONTRACT_SOLIDITY_IMPLEMENTER_NAME,
    CONTRACT_SOLIDITY_INTERFACE_NAME
)

CONTRACT_SOLIDITY_INTERFACE = """pragma solidity ^0.5.2;

interface {} {{
    function addOne(uint256 val) external;
    function getCount() external view returns (uint256);
}}
""".format(CONTRACT_SOLIDITY_INTERFACE_NAME)

USER_SCRIPT_1 = """

def main(contracts):
    print(contracts)
    test = contracts.get('Test')
    return test is not None and test.address is not None

"""

USER_SCRIPT_FAIL = """

def main(contracts):
    return False

"""

USER_SCRIPT_INVALID = """

# This is invalid
def main_func(contracts):
    return False

"""

HASHABLE_FILE = """Hello, world!
"""
HASHABLE_FILE_HASH = "09fac8dbfd27bd9b4d23a00eb648aa751789536d"

INVALID_JSON = """{ 'huuuRRRR'; durrr
"""
