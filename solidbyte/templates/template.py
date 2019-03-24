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
        """ Init the Template object.  Arguments can be added by subclasses.  The one used by
        Template are documented below.

        :param dir_mode: (:code:`int`) The directory mode permissions
        :param pwd: (:class:`pathlib.Path`) The current working directory
        """

        self.dir_mode = kwargs.get('dir_mode', 0o755)
        log.debug('Template dir_mode: {}'.format(self.dir_mode))
        self.pwd = to_path(kwargs.get('pwd') or Path.cwd())

        # The path of the directory of the class that sublclasses this class.  Should be the
        # template's __init__.py
        self.template_dir = Path(sys.modules[self.__module__].__file__).parent

    def initialize(self):
        """ This method performs all steps necessary to build a template.  It
        must be implemented by the Template subclass.
        """
        raise NotImplementedError("initialize() must be implemented for template")

    def copy_template_file(self, dest_dir, subdir, filename):
        """ Copy a file from the template module directory to dest

        :param dest_dir: (:class:`pathlib.Path`) - The destination directory in the project
            structure
        :param subdir: (:class:`pathlib.Path`) - The subdirectory under dest_dir
        :param filename: (:code:`str`) - The name of the destination file
        :returns: (:code:`str`) Destination path
        """

        dest_dir = to_path(dest_dir)

        source = self.template_dir.joinpath(subdir, filename)
        dest = dest_dir.joinpath(subdir, filename)
        log.info("Copying {} to {}...".format(filename, dest))
        return copyfile(source, dest)

    def create_dirs(self):
        """ Create the project directory structure """

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
