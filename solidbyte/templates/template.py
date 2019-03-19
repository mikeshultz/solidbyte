""" Abstract template class """
import sys
from shutil import copyfile
from pathlib import Path
from ..common.utils import to_path
from ..common.logging import getLogger

log = getLogger(__name__)


class Template(object):
    """ Template abstract """
    def __init__(self, *args, **kwargs):

        self.dir_mode = kwargs.get('dir_mode', 0o755)
        log.debug('Template dir_mode: {}'.format(self.dir_mode))
        self.pwd = to_path(kwargs.get('pwd') or Path.cwd())

        # The path of the directory of the class that sublclasses this class.  Should be the
        # template's __init__.py
        self.template_dir = Path(sys.modules[self.__module__].__file__).parent

    def initialize(self):
        raise NotImplementedError("initialize() must be implemented for template")

    def copy_template_file(self, dest_dir, subdir, filename):
        """ Copy a file from src to dest """

        dest_dir = to_path(dest_dir)

        source = self.template_dir.joinpath(subdir, filename)
        dest = dest_dir.joinpath(subdir, filename)
        log.info("Copying {} to {}...".format(filename, dest))
        return copyfile(source, dest)

    def create_dirs(self):

        tests_dir = self.pwd.joinpath('tests')
        contracts_dir = self.pwd.joinpath('contracts')
        deploy_dir = self.pwd.joinpath('deploy')
        scripts_dir = self.pwd.joinpath('scripts')

        if tests_dir.exists() \
                or contracts_dir.exists() \
                or deploy_dir.exists():
            raise FileExistsError("Project structure appears to already exist! Aborting...")

        log.info("Executing project initialization...")

        log.warning("Creating project directory structure with mode {0:o}".format(self.dir_mode))

        log.debug("Creating tests directory...")
        tests_dir.mkdir(mode=self.dir_mode)

        log.debug("Creating contracts directory...")
        contracts_dir.mkdir(mode=self.dir_mode)

        log.debug("Creating deploy directory...")
        deploy_dir.mkdir(mode=self.dir_mode)

        log.debug("Creating scripts directory...")
        scripts_dir.mkdir(mode=self.dir_mode)
