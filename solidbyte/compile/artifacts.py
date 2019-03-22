import json
from typing import Union, Optional, Any, Dict, Set
from pathlib import Path
from attrdict import AttrDict
from ..common.utils import to_path, to_path_or_cwd
from ..common.exceptions import SolidbyteException
from ..common.logging import getLogger

log = getLogger(__name__)

# Typing
PS = Union[Path, str]

# Module defs
ARTIFACT_CACHE: Set[Any] = set()


class CompiledContract:
    def __init__(self, name: str, artifact_path: PS) -> None:
        self.name = name
        self.artifact_path: PS = to_path(artifact_path)
        self.paths: AttrDict = AttrDict({
            'abi': self.artifact_path.joinpath('{}.abi'.format(self.name)),
            'bytecode': self.artifact_path.joinpath('{}.bin'.format(self.name)),
        })

        self.abi: Optional[Dict] = None
        self.bytecode: Optional[str] = None

        if not self._load_artifacts():
            log.warning("Loading of {} artifacts failed.".format(self.name))

    def __getitem__(self, key: str) -> Optional[Any]:
        """ Mostly for backwards compat, but allow this to be treated like a dict """
        if not hasattr(self, key):
            raise KeyError("Key {} not found".format(key))
        return getattr(self, key)

    def _load_artifacts(self) -> bool:
        """ Load the artifact files """

        # Load the bytecode
        with self.paths.bytecode.open() as _file:
            log.debug("Reading file {}...".format(self.paths.bytecode))
            self.bytecode = _file.read()

        # Load the ABI
        with self.paths.abi.open() as _file:
            log.debug("Reading file {}...".format(self.paths.abi))
            abi_str = _file.read()
            self.abi = json.loads(abi_str)

        return bool(self.abi or self.bytecode)


def available_contract_names(project_dir: PS) -> Set[str]:
    """ Return the names of all compiled contracts """
    project_dir = to_path_or_cwd(project_dir)

    builddir = project_dir.joinpath('build')
    if not builddir.is_dir():
        raise SolidbyteException("My word.  The build directory appears to be missing.")

    c_names = set()

    for d in builddir.iterdir():
        if d.is_dir() and (
                d.joinpath('{}.abi'.format(d.name)).is_file()
                or d.joinpath('{}.bin'.format(d.name)).is_file()
                ):
            c_names.add(d.name)

    return c_names


def contract_artifacts(name: str, project_dir: PS = None) -> CompiledContract:
    """ Return a CompiledContract object with the artifacts for a contract """
    project_dir = to_path_or_cwd(project_dir)
    builddir = project_dir.joinpath('build')
    artifact_path = builddir.joinpath(name)
    cc = CompiledContract(name=name, artifact_path=artifact_path)
    return cc


def artifacts(project_dir: PS) -> Set[Any]:
    """ Get the artifacts for all compiled contracts """

    project_dir = to_path_or_cwd(project_dir)
    contracts = available_contract_names(project_dir)

    artifacts = set()

    for contract in contracts:
        artifacts.add(contract_artifacts(contract, project_dir))

    return artifacts
