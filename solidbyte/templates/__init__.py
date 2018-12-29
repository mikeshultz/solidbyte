import sys
from importlib import import_module
from os import path, listdir
from ..common.logging import getLogger

log = getLogger(__name__)

"""
Templates
=========

Every template should at a minimum implement this function that returns an
instance of solidbyte.templates.Template or a derivative of:

    get_template_instance(*args, **kwargs)

For more details, see the Bare template.
TODO: Better docs
"""

TEMPLATE_DIR = path.join(path.dirname(__file__), 'templates')
TEMPLATES = {}


def lazy_load_templates(force_load=False):
    """ Import all templates and stuff them into TEMPLATES """
    if len(TEMPLATES.keys()) > 0 and not force_load:
        return TEMPLATES

    for d in listdir(TEMPLATE_DIR):
        log.debug("burp: {}".format(d))
        if path.isdir(path.join(TEMPLATE_DIR, d)):

            mod = None

            try:
                mod = import_module('.{}'.format(d), package='solidbyte.templates.templates')
                if hasattr(mod, 'get_template_instance'):
                    TEMPLATES[d] = mod
            except ImportError as e:
                # not a module, skip
                log.debug("sys.path: {}".format(sys.path))
                log.debug("Unable to import template module", exc_info=e)
                pass

    return TEMPLATES


# TODO: Depreciate
def get_templates():
    """ Return all available templates """
    log.debug("Loading templates from {}".format(TEMPLATE_DIR))
    return lazy_load_templates()


def init_template(name, dir_mode=0o755):
    """ Initialize and return a Template instance with name """

    lazy_load_templates()

    if name not in TEMPLATES:
        raise FileNotFoundError("Unknown template")

    return TEMPLATES[name].get_template_instance(dir_mode=dir_mode)
