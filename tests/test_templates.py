import pytest
from solidbyte.templates import (
    lazy_load_templates,
    get_templates,
    init_template,
)

from .const import TMP_DIR


def test_lazy_load_templates():
    templates = lazy_load_templates()
    templates2 = lazy_load_templates()
    assert id(templates) == id(templates2)
    assert templates.get('bare') is not None
    assert templates.get('erc20') is not None


def test_get_templates():
    """ TO BE DEPRECIATD """
    templates = lazy_load_templates()
    templates2 = get_templates()
    assert id(templates) == id(templates2)


@pytest.mark.parametrize("template_name", [
    'bare',
    'erc20',
])
def test_init_template(template_name):

    # Setup the test dir
    workdir = TMP_DIR.joinpath('template-test-{}'.format(template_name))
    workdir.mkdir(parents=True)

    # Get the Template object
    tmpl = init_template(template_name)

    # For testing, override pwd
    tmpl.pwd = workdir

    assert hasattr(tmpl, 'initialize'), "All templates must implement initialize()"
    tmpl.initialize()

    # All of these need to be part of the template, even if empty
    assert workdir.joinpath('tests').is_dir()
    assert workdir.joinpath('contracts').is_dir()
    assert workdir.joinpath('deploy').is_dir()
    assert workdir.joinpath('networks.yml').is_file()
