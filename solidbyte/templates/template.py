""" Abstract template class """
from os import path, mkdir, getcwd
from pathlib import Path
from ..common.logging import getLogger, parent_logger

log = getLogger(__name__)

class Template(object):
    """ Template abstract """
    def __init__(self, *args, **kwargs):

        self.dir_mode = kwargs.get('dir_mode', 0o755)
        self.pwd = Path(getcwd())

    def initialize(self):
        raise NotImplemented("initialize() must be implemented for template")

    def create_dirs(self):

        tests_dir = self.pwd.joinpath('tests')
        contracts_dir = self.pwd.joinpath('contracts')
        deploy_dir = self.pwd.joinpath('deploy')

        if tests_dir.exists() \
            or contracts_dir.exists() \
            or deploy_dir.exists():
            raise FileExistsError("Project structure appears to already exist! Aborting...")

        log.info("Executing project initialization...")

        log.warn("Creating project directory structure with mode {0:o}".format(self.dir_mode))

        log.debug("Creating tests directory...")
        tests_dir.mkdir(mode=self.dir_mode)

        log.debug("Creating contracts directory...")
        contracts_dir.mkdir(mode=self.dir_mode)

        log.debug("Creating deploy directory...")
        deploy_dir.mkdir(mode=self.dir_mode)