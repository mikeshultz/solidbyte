""" Test the artifact functions and objects """
from solidbyte.compile import Compiler
from solidbyte.compile.artifacts import (
    artifacts,
    contract_artifacts,
    available_contract_names,
    CompiledContract,
)


def test_CompiledContract(mock_project):
    """ test the CompiledContract object """
    with mock_project() as mock:
        contract_name = 'Test'

        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        cc = CompiledContract(name=contract_name,
                              artifact_path=mock.paths.build.joinpath(contract_name))
        assert cc.abi
        assert cc.bytecode


def test_available_contract_names(mock_project):
    """ test the available_contract_names function """
    with mock_project() as mock:
        contract_name = 'Test'

        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        names = available_contract_names(mock.paths.project)
        assert contract_name in names


def test_contract_artifacts(mock_project):
    """ test the contract_artifacts function """
    with mock_project() as mock:
        contract_name = 'Test'

        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        cc = contract_artifacts(contract_name, mock.paths.project)
        assert isinstance(cc, CompiledContract)
        assert cc.abi
        assert cc.bytecode


def test_artifacts(mock_project):
    """ test the artifacts function """
    with mock_project() as mock:
        contract_name = 'Test'

        compiler = Compiler(project_dir=mock.paths.project)
        compiler.compile_all()

        all_artifacts = artifacts(mock.paths.project)
        assert type(all_artifacts) == set
        found = False
        for cc in all_artifacts:
            assert isinstance(cc, CompiledContract)
            if cc.name == contract_name:
                found = True
        assert found
