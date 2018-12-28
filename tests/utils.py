import re
import pytest
from pathlib import Path
from datetime import datetime
from web3 import Web3

TMP_DIR = Path('/tmp/solidbyte-test-{}'.format(datetime.now().timestamp()))


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
    if type(s) == 'bytes':
        s = s.decode('utf-8')
    assert type(s) == str
    return re.match(r'^[A-Fa-f0-9]+$', s) is not None
