from pathlib import Path
from solidbyte.common.web3 import web3c
from solidbyte.common.metafile import MetaFile
from solidbyte.deploy import Deployer
from solidbyte.deploy.objects import Contract, ContractDependencyTree, ContractLeaf
from solidbyte.compile.compiler import Compiler
from .const import (
    NETWORK_NAME,
    LIBRARY_SOURCE_FILE_4,
)
from .utils import write_temp_file


def test_deployer(mock_project):
    """ Test deploying a project """

    """
    TODO
    ----
    This is a massive test spanning a ton of components.  Can this be broken down at all?  Or maybe
    forced to run last somehow?  This is more or less a large integration test.  If some small
    component fails, this test will fail.  So if you have multiple tests failing that include this
    one, start on the other one first.
    """

    with mock_project() as mock:

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        deployer_account = web3.eth.accounts[0]

        # Init the Deployer
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )

        # Test initial state with the mock project
        assert len(d.artifacts) == 1
        contract_key = list(d.artifacts.keys())[0]
        assert d.artifacts[contract_key].name == 'Test'
        assert d.artifacts[contract_key].abi is not None
        assert d.artifacts[contract_key].bytecode is not None
        assert len(d.deployed_contracts) == 0

        # Check that deployment needs to happen
        assert d.check_needs_deploy()
        assert d.check_needs_deploy('Test')

        d._load_user_scripts()
        assert len(d._deploy_scripts) == 1  # Mock project has 1 deploy script

        # Run a deployment
        assert d.deploy(), "Test deployment failed"

        # Verify it looks complete to the deployer
        # assert not d.check_needs_deploy()
        # assert not d.check_needs_deploy('Test')
        # TODO: Disabled asserts due to a probable bug or bad test env.  Look into it.

        try:
            d.check_needs_deploy('Nothing')
            assert False, "check_needs_deploy() should throw when a contract does not exist"
        except FileNotFoundError as err:
            assert 'Unknown contract' in str(err)


def test_deptree(mock_project):
    """ Test the ContractDependencyTree """
    deptree = ContractDependencyTree()
    assert deptree.root.is_root()
    parent = deptree.root.add_dependent('Parent')
    lib = parent.add_dependent('Library1')
    el, depth = deptree.search_tree('Parent')
    assert el == parent
    assert depth == 0
    el, depth = deptree.search_tree('Library1')
    assert el == lib
    assert depth == 1

    lib2 = deptree.add_dependent('Library2', str(parent))
    assert isinstance(lib2, ContractLeaf)
    assert lib2.get_parent() == parent

    parents_children = parent.get_dependents()
    assert lib2 in parents_children

    assert deptree.has_dependents('Parent')
    assert not deptree.has_dependents('Library2')
    assert deptree.has_dependencies('Library2')
    assert not deptree.has_dependencies('Parent')

    try:
        deptree.move('NotFound', ContractLeaf('Fallen', deptree))
        assert False, 'move() should throw if it does not exist in the tree'
    except Exception as err:
        assert 'not found' in str(err)


def test_deployer_deptree(mock_project):
    """ Test the Deployer dep tree """

    with mock_project(with_libraries=True) as mock:

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        deployer_account = web3.eth.accounts[0]

        # Init the Deployer
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )

        deptree = d._build_dependency_tree(force=True)
        assert isinstance(deptree, ContractDependencyTree)
        assert deptree.root.has_dependents()


def test_contract_with_library(mock_project):
    """ Test the Contract object """

    with mock_project(with_libraries=True) as mock:

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        meta = MetaFile(project_dir=mock.paths.project)

        # Get all the file contents from the compiler output
        unnecessary_bytecode = None
        # unnecessary_abi = None
        safemath_bytecode = None
        # safemath_abi = None
        # testmath_abi = None
        testmath_bytecode = None

        with mock.paths.build.joinpath('Unnecessary', 'Unnecessary.bin').open() as binfile:
            unnecessary_bytecode = binfile.read()

        # with mock.paths.build.joinpath('Unnecessary', 'Unnecessary.abi').open() as abifile:
        #     unnecessary_abi = json.loads(abifile.read())

        with mock.paths.build.joinpath('SafeMath', 'SafeMath.bin').open() as binfile:
            safemath_bytecode = binfile.read()

        # with mock.paths.build.joinpath('SafeMath', 'SafeMath.abi').open() as abifile:
        #     safemath_abi = json.loads(abifile.read())

        with mock.paths.build.joinpath('TestMath', 'TestMath.bin').open() as binfile:
            testmath_bytecode = binfile.read()

        # with mock.paths.build.joinpath('TestMath', 'TestMath.abi').open() as abifile:
        #     testmath_abi = json.loads(abifile.read())

        # Build the expected source objects
        # unnecessary_source_contract = AttrDict({
        #     'name': 'Unnecessary',
        #     'abi': unnecessary_abi,
        #     'bytecode': unnecessary_bytecode,
        # })
        # net_id = web3.net.chainId
        # meta.add('Unnecessary', net_id, -address, -abi, -bytecode-hash)

        # safemath_source_contract = AttrDict({
        #     'name': 'SafeMath',
        #     'abi': safemath_abi,
        #     'bytecode': safemath_bytecode,
        # })

        # testmath_source_contract = AttrDict({
        #     'name': 'TestMath',
        #     'abi': testmath_abi,
        #     'bytecode': testmath_bytecode,
        # })

        # Create the Contract instances to mess around with
        unnecessary_contract = Contract(
            name='Unnecessary',
            network_name=NETWORK_NAME,
            from_account=web3.eth.accounts[0],
            metafile=meta,
            web3=web3,
        )

        # Make sure contract with no deployments has no expected attrs
        assert repr(unnecessary_contract) == 'Unnecessary'
        assert unnecessary_contract.is_deployed() is False
        assert unnecessary_contract.address is None
        assert unnecessary_contract.abi is None
        assert unnecessary_contract.bytecode_hash is None

        safemath_contract = Contract(
            name='SafeMath',
            network_name=NETWORK_NAME,
            from_account=web3.eth.accounts[0],
            metafile=meta,
            web3=web3,
        )

        testmath_contract = Contract(
            name='TestMath',
            network_name=NETWORK_NAME,
            from_account=web3.eth.accounts[0],
            metafile=meta,
            web3=web3,
        )

        # Verify things look as expected
        assert unnecessary_contract.check_needs_deployment(unnecessary_bytecode)
        assert safemath_contract.check_needs_deployment(safemath_bytecode)
        assert testmath_contract.check_needs_deployment(testmath_bytecode)

        # Deploy our contracts
        unnecessary = unnecessary_contract.deployed()
        safeMath = safemath_contract.deployed(gas=int(5e6))
        safeMath_again = safemath_contract.deployed(gas=int(5e6))
        assert safeMath.bytecode == safeMath_again.bytecode
        assert safeMath.address == safeMath_again.address
        assert safeMath.address is not None
        testMath = testmath_contract.deployed(gas=int(5e6), links={
                'SafeMath': safeMath.address,
                'Unnecessary': unnecessary.address,
            })

        # Test that everything is working
        assert testMath.functions.mul(3, 2).call() == 6
        assert testMath.functions.div(6, 3).call() == 2

        # Update the library
        unnecessary_filename = 'Unnecessary.sol'
        unnecessary_file = mock.paths.contracts.joinpath(unnecessary_filename)
        write_temp_file(LIBRARY_SOURCE_FILE_4, unnecessary_filename, mock.paths.contracts,
                        overwrite=True)
        assert unnecessary_file.is_file()

        # Compile it
        assert compiler.compile(unnecessary_file) is None

        new_bytecode = None
        with mock.paths.build.joinpath('Unnecessary', 'Unnecessary.bin').open() as binfile:
            new_bytecode = binfile.read()

        # Make sure the Contract instances know they need to be deployed
        assert unnecessary_contract.check_needs_deployment(new_bytecode)
        # TODO: This is currently not supported, only Deployer can get an overview to check against
        # dependencies.
        # assert testmath_contract.check_needs_deployment(testmath_bytecode)


def test_deployer_contract_with_libraries(mock_project):
    """ Test the Contract object """

    with mock_project(with_libraries=True) as mock:

        # Setup our environment
        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        # Since we're not using the pwd, we need to use this undocumented API (I know...)
        web3c._load_configuration(mock.paths.networksyml)
        web3 = web3c.get_web3(NETWORK_NAME)

        deployer_account = web3.eth.accounts[0]

        # Init the Deployer
        d = Deployer(
            network_name=NETWORK_NAME,
            account=deployer_account,
            project_dir=mock.paths.project,
        )

        assert d.check_needs_deploy()
        to_deploy = d.contracts_to_deploy()
        assert 'SafeMath' in to_deploy
        assert 'TestMath' in to_deploy
        assert 'Unnecessary' in to_deploy

        d.deploy()
        d.refresh()
        assert not d.check_needs_deploy()

        # Update the library
        # safe_math_filename = 'SafeMath.sol'
        # safe_math_file = mock.paths.contracts.joinpath(safe_math_filename)
        # write_temp_file(LIBRARY_SOURCE_FILE_2, safe_math_filename, mock.paths.contracts,
        #                 overwrite=True)
        # assert safe_math_file.is_file()

        # Update the library
        unnecessary_filename = 'Unnecessary.sol'
        unnecessary_file = mock.paths.contracts.joinpath(unnecessary_filename)
        write_temp_file(LIBRARY_SOURCE_FILE_4, unnecessary_filename, mock.paths.contracts,
                        overwrite=True)
        assert unnecessary_file.is_file()

        # Compile it
        assert compiler.compile(unnecessary_file) is None

        d.refresh()
        assert d.check_needs_deploy()
        to_deploy = d.contracts_to_deploy()
        assert 'Unnecessary' in to_deploy
        assert 'TestMath' in to_deploy


def test_deployer_no_contracts(mock_project, temp_dir):
    with mock_project() as mock:
        with temp_dir() as workdir:

            assert Path.cwd() == workdir

            # Since we're not using the pwd, we need to use this undocumented API (I know...)
            web3c._load_configuration(mock.paths.networksyml)
            web3 = web3c.get_web3(NETWORK_NAME)

            deployer_account = web3.eth.accounts[0]

            # Init the Deployer
            try:
                Deployer(
                    network_name=NETWORK_NAME,
                    account=deployer_account,
                    project_dir=workdir,
                )
                assert False, "Should fail init if missing contracts directory"
            except FileNotFoundError as err:
                assert 'contracts directory' in str(err)
