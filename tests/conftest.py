import pytest
from datetime import datetime
from contextlib import contextmanager
from solidbyte.common.logging import setDebugLogging
from .const import TMP_DIR
from .utils import create_mock_project, delete_path_recursively


def pytest_sessionstart(session):
    """ before session.main() is called. """
    setDebugLogging()


@pytest.fixture
def mock_project():
    @contextmanager
    def yield_mock_project(tmpdir=TMP_DIR):
        project_dir = tmpdir.joinpath('project-{}'.format(datetime.now().timestamp()))
        create_mock_project(project_dir)
        yield project_dir
        delete_path_recursively(project_dir)
    return yield_mock_project
