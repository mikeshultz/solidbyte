""" Create a bare project template """
from .template import Template

class BareTemplate(Template):
    def __init__(self, *args, **kwargs):
        super(BareTemplate, self).__init__(*args, **kwargs)

    def initialize(self):
        """ Create a bare project structure """
        self.create_dirs()