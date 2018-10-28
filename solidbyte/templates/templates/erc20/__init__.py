""" Create a project template with an ERC20 contract and accompanying tests """
from os import path
from pathlib import Path
from ...template import Template
from ....common.logging import getLogger

log = getLogger(__name__)

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

        self.copy_template_file(self.pwd, 'contracts', 'ERC20.sol')
        self.copy_template_file(self.pwd, 'contracts', 'IERC20.sol')
        self.copy_template_file(self.pwd, 'contracts', 'SafeMath.sol')

    def create_deployment(self):
        """ Create the deploy file """

        log.info("Creating contract deploy scripts...")

        self.copy_template_file(self.pwd, 'deploy', '__init__.py')
        self.copy_template_file(self.pwd, 'deploy', 'deploy_main.py')

def get_template_instance(*args, **kwargs):
    return ERC20Template(*args, **kwargs)
