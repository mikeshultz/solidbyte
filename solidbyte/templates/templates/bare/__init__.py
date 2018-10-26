""" Create a bare project template """
from ...template import Template

class BareTemplate(Template):
    def __init__(self, *args, **kwargs):
        super(BareTemplate, self).__init__(*args, **kwargs)

    def initialize(self):
        """ Create a bare project structure """
        self.create_dirs()
        self.create_deployment()

    def create_deployment(self):
        """ Create the deploy file """

        log.info("Creating contract deploy scripts...")

        copy_template_file(self.pwd, 'deploy', '__init__.py')
        copy_template_file(self.pwd, 'deploy', 'deploy_main.py')

def get_template_instance(*args, **kwargs):
    return BareTemplate(*args, **kwargs)