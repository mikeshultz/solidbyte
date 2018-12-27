""" Create a bare project template """
from ...template import Template
from ....common.logging import getLogger

log = getLogger(__name__)


class BareTemplate(Template):
    def __init__(self, *args, **kwargs):
        super(BareTemplate, self).__init__(*args, **kwargs)

    def initialize(self):
        """ Create a bare project structure """
        self.create_dirs()
        self.create_deployment()
        self.create_networks()

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
    return BareTemplate(*args, **kwargs)
