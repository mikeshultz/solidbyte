import pytest
from solidbyte.templates import (
    lazy_load_templates,
    get_templates,
    init_template,
)
from solidbyte.templates.template import Template


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
def test_init_template(template_name, temp_dir):

    with temp_dir() as tmp:

        # Get the Template object
        tmpl = init_template(template_name, pwd=tmp)

        # For testing, override pwd
        tmpl.pwd = tmp

        assert hasattr(tmpl, 'initialize'), "All templates must implement initialize()"
        tmpl.initialize()

        # All of these need to be part of the template, even if empty
        assert tmp.joinpath('tests').is_dir()
        assert tmp.joinpath('contracts').is_dir()
        assert tmp.joinpath('deploy').is_dir()
        assert tmp.joinpath('networks.yml').is_file()


@pytest.mark.parametrize("template_name", [
    'bare',
    'erc20',
])
def test_template_required_methods(template_name):
    """ Make sure the templates all have the rquired methods """

    templates = lazy_load_templates()
    tmpl_module = templates.get(template_name)
    assert tmpl_module is not None
    assert hasattr(tmpl_module, 'get_template_instance')

    tmpl = tmpl_module.get_template_instance()
    assert isinstance(tmpl, Template)
    assert hasattr(tmpl, 'initialize'), "initialize() must be implemented in Template"


@pytest.mark.parametrize("template_name", [
    'bare',
    'erc20',
])
def test_template_required_files(template_name):
    """ Make sure the templates all have the rquired files """

    templates = lazy_load_templates()
    tmpl_module = templates.get(template_name)
    assert tmpl_module is not None
    assert hasattr(tmpl_module, 'get_template_instance')

    tmpl = tmpl_module.get_template_instance()
    assert isinstance(tmpl, Template)
    assert hasattr(tmpl, 'template_dir'), "Template should have the template_dir defined"
    assert tmpl.template_dir.joinpath('__init__.py').exists(), "Template needs to be a module"

    deploy_dir = tmpl.template_dir.joinpath('deploy')
    assert deploy_dir.exists(), "Template must have a deploy directory"
    assert deploy_dir.is_dir(), "Template must have a deploy directory"

    # Only the bare template does not need these
    if template_name != 'bare':
        contracts_dir = tmpl.template_dir.joinpath('contracts')
        tests_dir = tmpl.template_dir.joinpath('tests')
        assert contracts_dir.exists(), "Template must have a contracts directory"
        assert contracts_dir.is_dir(), "Template must have a contracts directory"
        assert tests_dir.exists(), "Template must have a tests directory"
        assert tests_dir.is_dir(), "Template must have a tests directory"


@pytest.mark.parametrize("template_name", [
    'bare',
    'erc20',
])
def test_template_init(template_name, temp_dir):
    """ Make sure the templates create the required project structure """

    with temp_dir() as tmp:
        project_dir = tmp

        templates = lazy_load_templates()
        tmpl_module = templates.get(template_name)
        assert tmpl_module is not None
        assert hasattr(tmpl_module, 'get_template_instance')

        tmpl = tmpl_module.get_template_instance(pwd=project_dir)
        assert isinstance(tmpl, Template)
        assert hasattr(tmpl, 'initialize'), "Template should have the initialize implemented"
        assert hasattr(tmpl, 'pwd'), "Template should have the pwd defined"
        assert tmpl.pwd == project_dir

        # Init
        tmpl.initialize()

        # The required files and dirs a template should create
        assert project_dir.joinpath('deploy').is_dir()
        assert project_dir.joinpath('contracts').is_dir()
        assert project_dir.joinpath('tests').is_dir()
        assert project_dir.joinpath('networks.yml').is_file()
