""" Abstract template class """
from os import path, mkdir, getcwd
from ..common.logging import getLogger, parent_logger

log = getLogger(__name__)

class Template(object):
    """ Template abstract """
    def __init__(self, *args, **kwargs):

        self.dir_mode = kwargs.get('dir_mode', 0o755)
        self.pwd = getcwd()

    def initialize(self):
        raise NotImplemented("initialize() must be implemented for template")

    def create_dirs(self):

        if path.isdir(path.join(self.pwd, 'tests')) \
            or path.isdir(path.join(self.pwd, 'contracts')):
            raise FileExistsError("Project structure appears to already exist! Aborting...")

        log.info("Executing project initialization...")

        log.warn("Creating project directory structure with mode {0:o}".format(self.dir_mode))

        log.debug("Creating tests directory...")
        mkdir(path.join(self.pwd, 'tests'), mode=self.dir_mode)

        log.debug("Creating contracts directory...")
        mkdir(path.join(self.pwd, 'contracts'), mode=self.dir_mode)