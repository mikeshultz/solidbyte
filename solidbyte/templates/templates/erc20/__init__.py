""" Create a project template with an ERC20 contract and accompanying tests """
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
        self.create_networks()

    def create_tests(self):
        """ Create the test files """

        self.copy_template_file(self.pwd, 'tests', 'test_erc20.py')

    def create_contracts(self):
        """ Create the test files """

        log.info("Creating contract templates...")

        self.copy_template_file(self.pwd, 'contracts', 'MyERC20.sol')
        self.copy_template_file(self.pwd, 'contracts', 'ERC20.sol')
        self.copy_template_file(self.pwd, 'contracts', 'IERC20.sol')
        self.copy_template_file(self.pwd, 'contracts', 'SafeMath.sol')

    def create_deployment(self):
        """ Create the deploy file """

        log.info("Creating contract deploy scripts...")

        self.copy_template_file(self.pwd, 'deploy', '__init__.py')
        self.copy_template_file(self.pwd, 'deploy', 'deploy_main.py')

    def create_networks(self):
        """ Create the networks.yml file """

        log.info("Creating networks.yml...")

        self.copy_template_file(self.pwd, '', 'networks.yml')


def get_template_instance(*args, **kwargs):
    return ERC20Template(*args, **kwargs)
