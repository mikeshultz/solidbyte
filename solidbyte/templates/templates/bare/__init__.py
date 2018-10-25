""" Create a bare project template """
from ...template import Template

class BareTemplate(Template):
    def __init__(self, *args, **kwargs):
        super(BareTemplate, self).__init__(*args, **kwargs)

    def initialize(self):
        """ Create a bare project structure """
        self.create_dirs()

def get_template_instance(*args, **kwargs):
    return BareTemplate(*args, **kwargs)