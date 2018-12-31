""" Abstract template class """
import sys
from os import path, getcwd
from shutil import copyfile
from pathlib import Path
from ..common.logging import getLogger

log = getLogger(__name__)


class Template(object):
    """ Template abstract """
    def __init__(self, *args, **kwargs):

        self.dir_mode = kwargs.get('dir_mode', 0o755)
        self.pwd = kwargs.get('pwd', Path(getcwd()))
        self.template_dir = Path(path.dirname(sys.modules[self.__module__].__file__))
        print(self.template_dir)

    def initialize(self):
        raise NotImplementedError("initialize() must be implemented for template")

    def copy_template_file(self, dest_dir, subdir, filename):
        """ Copy a file from src to dest """

        if type(dest_dir) == str:
            dest_dir = Path(dest_dir)
        if type(subdir) == str:
            subdir = Path(subdir)

        source = self.template_dir.joinpath(subdir, filename)
        dest = dest_dir.joinpath(subdir, filename)
        log.info("Copying {} to {}...".format(filename, dest))
        return copyfile(source, dest)

    def create_dirs(self):

        tests_dir = self.pwd.joinpath('tests')
        contracts_dir = self.pwd.joinpath('contracts')
        deploy_dir = self.pwd.joinpath('deploy')

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
