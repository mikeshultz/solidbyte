""" Create a project template with an ERC20 contract and accompanying tests """
from os import path
from pathlib import Path
from shutil import copyfile
from ...template import Template
from ....common.logging import getLogger, parent_logger

log = getLogger(__name__)
TEMPLATE_DIR = Path(path.dirname(__file__))

def copy_template_file(dest_dir, subdir, filename):
    """ Copy a file from src to dest """

    if type(dest_dir) == str:
        dest_dir = Path(dest_dir)
    if type(subdir) == str:
        subdir = Path(subdir)

    source = TEMPLATE_DIR.joinpath(subdir, filename)
    dest = dest_dir.joinpath(subdir, filename)
    log.info("Copying {} to {}...".format(filename, dest))
    return copyfile(source, dest)

class ERC20Template(Template):
    def __init__(self, *args, **kwargs):
        super(ERC20Template, self).__init__(*args, **kwargs)

    def initialize(self):
        """ Create a bare project structure """
        self.create_dirs()
        self.create_tests()
        self.create_contracts()
        self.create_deployment()

    def create_tests(self):
        """ Create the test files """

        copy_template_file(self.pwd, 'tests', 'test_erc20.py')

    def create_contracts(self):
        """ Create the test files """

        log.info("Creating contract templates...")

        copy_template_file(self.pwd, 'contracts', 'ERC20.sol')
        copy_template_file(self.pwd, 'contracts', 'IERC20.sol')
        copy_template_file(self.pwd, 'contracts', 'SafeMath.sol')

    def create_deployment(self):
        """ Create the deploy file """

        log.info("Creating contract deploy scripts...")

        copy_template_file(self.pwd, 'deploy', '__init__.py')
        copy_template_file(self.pwd, 'deploy', 'deploy_main.py')

def get_template_instance(*args, **kwargs):
    return ERC20Template(*args, **kwargs)
