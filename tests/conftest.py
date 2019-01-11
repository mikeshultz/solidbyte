import os
import pytest
from pathlib import Path
from datetime import datetime
from attrdict import AttrDict
from contextlib import contextmanager
from solidbyte.common.logging import setDebugLogging
from .const import TMP_DIR
from .utils import (
    create_mock_project,
    create_mock_project_with_libraries,
    delete_path_recursively,
    setup_venv_with_solidbyte,
)


def pytest_sessionstart(session):
    """ before session.main() is called. """
    setDebugLogging()


@pytest.fixture
def mock_project():
    @contextmanager
    def yield_mock_project(tmpdir=TMP_DIR, with_libraries=False):
        project_dir = tmpdir.joinpath('project-{}'.format(datetime.now().timestamp()))
        # Explicitly set the project directory for the session.
        # Doesn't work? store.set(store.Keys.PROJECT_DIR, project_dir)
        if with_libraries:
            create_mock_project_with_libraries(project_dir)
        else:
            create_mock_project(project_dir)
        original_pwd = Path.cwd()
        os.chdir(project_dir)
        yield AttrDict({
                'paths': AttrDict({
                        'project': project_dir,
                        'tests': project_dir.joinpath('tests'),
                        'contracts': project_dir.joinpath('contracts'),
                        'deploy': project_dir.joinpath('deploy'),
                        'build': project_dir.joinpath('build'),
                        'networksyml': project_dir.joinpath('networks.yml'),
                    })
            })
        os.chdir(original_pwd)
        delete_path_recursively(project_dir)
    return yield_mock_project


@pytest.fixture
def temp_dir():
    @contextmanager
    def yield_temp_dir(tmpdir=TMP_DIR):
        temp_dir = tmpdir.joinpath('temp-{}'.format(datetime.now().timestamp()))
        temp_dir.mkdir(parents=True)
        original_pwd = Path.cwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_pwd)
        delete_path_recursively(temp_dir)
    return yield_temp_dir


@pytest.fixture
def virtualenv():
    """ This has some issues on Travis.  TODO: Maybe look into this at some point """
    @contextmanager
    def yield_venv(tmpdir=TMP_DIR):
        venv_dir = tmpdir.joinpath('venv-{}'.format(datetime.now().timestamp()))
        python = setup_venv_with_solidbyte(venv_dir)
        assert venv_dir.joinpath('bin', 'activate').is_file(), "Invalid venv created"
        yield AttrDict({
                'paths': AttrDict({
                        'python': python,
                        'venv': venv_dir,
                        'activate': venv_dir.joinpath('bin', 'activate'),
                    })
            })
        delete_path_recursively(venv_dir)
    return yield_venv
