import re
import pytest
from pathlib import Path
from web3 import Web3
from hexbytes import HexBytes
from .const import (
    TMP_DIR,
    CONTRACT_DIR,
    DEPLOY_DIR,
    NETWORKS_YML_1,
    CONTRACT_SOURCE_FILE_1,
    CONTRACT_DEPLOY_SCRIPT_1,
)


def write_temp_file(txt, fname=None, directory=None, overwrite=False):
    tmp_dir = directory or TMP_DIR
    tmp_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    filename = fname or '{}.{}'.format(Web3.sha3(text=txt).hex(), 'tmp')
    file_path = tmp_dir.joinpath(filename)

    if overwrite:
        open_mode = 'w'
    else:
        open_mode = 'x'

    with file_path.open(mode=open_mode) as tmpfile:
        tmpfile.write(txt)

    return file_path


@pytest.fixture(scope='session', autouse=True)
def cleanupdir(path=None):
    if path is None:
        path = TMP_DIR
    if path.exists() and path.is_dir:
        for fil in path.iterdir():
            if fil.is_dir():
                cleanupdir(fil)
            else:
                fil.unlink()
        path.rmdir()
    else:
        raise ValueError("not a directory")


def get_file_extension(fil):
    parts = fil.name.split('.')
    assert len(parts) > 1, "Invalid filename.  No extension."
    return parts[-1]


def is_hex(s):
    """ Check if a string is hex """
    if type(s) == bytes:
        s = s.decode('utf-8')
    elif isinstance(s, HexBytes):
        s = s.hex()
    assert type(s) == str
    return re.match(r'^(0x)*[A-Fa-f0-9]+$', s) is not None


def create_mock_project(project_dir):
    """ Create a mock project with a contract, and deploy script """
    assert isinstance(project_dir, Path), "project_dir needs to be a Path object"

    contract_dir = project_dir.joinpath('contracts')
    deploy_dir = project_dir.joinpath('deploy')

    project_dir.mkdir(parents=True, mode=0o755, exist_ok=True)
    contract_dir.mkdir(parents=True, mode=0o755, exist_ok=True)
    deploy_dir.mkdir(parents=True, mode=0o755, exist_ok=True)

    write_temp_file(NETWORKS_YML_1, 'networks.yml', project_dir)
    write_temp_file(CONTRACT_SOURCE_FILE_1, 'Test.sol', contract_dir)
    write_temp_file(CONTRACT_DEPLOY_SCRIPT_1, 'deploy_main.py', deploy_dir)
