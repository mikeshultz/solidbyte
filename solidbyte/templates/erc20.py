""" Create a project template with an ERC20 contract and accompanying tests """
from os import path
from shutil import copyfile
from .template import Template
from ..common.logging import getLogger, parent_logger

log = getLogger(__name__)
HERE = path.dirname(__file__)
TEMPLATE_DIR = path.join(HERE, 'files')

def copy_template_file(dest_dir, subdir, filename):
    """ Copy a file from src to dest """
    source = path.join(TEMPLATE_DIR, subdir, filename)
    dest = path.join(dest_dir, subdir, filename)
    log.info("Copying {} to {}...".format(filename, dest))
    return copyfile(source, dest)

class ERC20Template(Template):
    def __init__(self, *args, **kwargs):
        super(ERC20Template, self).__init__(*args, **kwargs)

    def initialize(self):
        """ Create a bare project structure """
        self.create_dirs()
        #self.create_tests()
        self.create_contracts()

    def create_tests(self):
        """ Create the test files """
        raise NotImplementedError("TODO")

    def create_contracts(self):
        """ Create the test files """

        log.info("Creating contract templates...")

        # Copy the contract templates
        copy_template_file(self.pwd, 'contracts', 'ERC20.sol')
        copy_template_file(self.pwd, 'contracts', 'IERC20.sol')
        copy_template_file(self.pwd, 'contracts', 'SafeMath.sol')

        # Copy the accompanying tests
        copy_template_file(self.pwd, 'tests', 'test_erc20.py')
