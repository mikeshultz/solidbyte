import re
import pytest
import hashlib
from subprocess import Popen, PIPE
from pathlib import Path
from datetime import datetime
from web3 import Web3
from hexbytes import HexBytes
from .const import (
    TMP_DIR,
    NETWORKS_YML_1,
    CONTRACT_SOURCE_FILE_1,
    CONTRACT_DEPLOY_SCRIPT_1,
    PYTEST_TEST_1,
)

RECURSUION_MAX = 15


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
    test_dir = project_dir.joinpath('tests')

    project_dir.mkdir(parents=True, mode=0o755, exist_ok=True)
    contract_dir.mkdir(parents=True, mode=0o755, exist_ok=True)
    deploy_dir.mkdir(parents=True, mode=0o755, exist_ok=True)

    write_temp_file(NETWORKS_YML_1, 'networks.yml', project_dir)
    write_temp_file(CONTRACT_SOURCE_FILE_1, 'Test.sol', contract_dir)
    write_temp_file(CONTRACT_DEPLOY_SCRIPT_1, 'deploy_main.py', deploy_dir)
    write_temp_file(PYTEST_TEST_1, 'test_testing.py', test_dir)


def delete_path_recursively(pth, depth=0):
    """ Delete a path and everything under it """
    assert isinstance(pth, Path)
    assert str(pth).startswith('/tmp')  # Only temp files.
    if depth > RECURSUION_MAX:
        raise Exception('Max recursion depth!')
    if not pth.exists():
        return False
    if pth.is_file() or pth.is_symlink():
        pth.unlink()
    elif pth.is_dir():
        for child in pth.iterdir():
            delete_path_recursively(child, depth+1)
        pth.rmdir()
    else:
        raise Exception("Unable to remove {}".format(str(pth)))


def create_venv(loc=None):
    """ Create a python virtualenv """
    if loc is None:
        loc = TMP_DIR.joinpath('venv-{}'.format(datetime.now().timestamp()))
    loc.mkdir(parents=True)
    assert loc.is_dir(), "Venv dir not created properly"
    cmd = ['python', '-m', 'venv', str(loc)]
    proc = Popen(cmd, stdout=PIPE)
    proc.wait()
    if proc.returncode != 0:
        raise Exception("Unable to create test venv")
    assert loc.joinpath('bin').is_dir(), "bin directory is missing from venv {}".format(loc)
    assert loc.joinpath('bin', 'python').exists(), "python is missing from venv {}".format(loc)
    return loc


def pip_install(python):
    assert python.exists(), "python not found"
    cmd = [str(python), '-m', 'pip', 'install', '.']
    proc = Popen(cmd)
    proc.wait()
    if proc.returncode != 0:
        return False
    return True


def setup_venv_with_solidbyte(loc=None):
    """ Install solidbyte to a venv """
    venv_path = create_venv(loc)
    python = venv_path.joinpath('bin', 'python')
    setuppy = Path.cwd().joinpath('setup.py')
    assert setuppy.is_file(), "unable to find Solidbyte's setup.py"
    assert pip_install(python), "Install of solidbyte failed"
    return python
