import copy
from solidbyte.common.networks import NetworksYML
from solidbyte.common.exceptions import ConfigurationError
from .const import NETWORK_NAME, NETWORKS_YML_2, NETWORKS_YML_NOCONFIG


def test_networksyml(mock_project):
    """ Make sure the config is loaded and it's what we expect """

    with mock_project() as mock:
        yml = NetworksYML(project_dir=mock.paths.project)

        # Make sure the test network exists
        assert yml.network_config_exists(NETWORK_NAME)

        # Load it and verify
        test_config = yml.get_network_config(NETWORK_NAME)
        assert test_config.get('type') == 'eth_tester'
        assert test_config.get('autodeploy_allowed') is True

        # Check the autodeploy_allowed method
        assert yml.autodeploy_allowed(NETWORK_NAME) is True


def test_networksyml_noload(mock_project):
    """ test that no_load works and that other config files can be operated """

    with mock_project() as mock:
        yml = NetworksYML(no_load=True)

        assert yml.config is None
        assert yml.networks == []

        # Write the config file we're going to parse
        config_file = mock.paths.project.joinpath('networks2.yml')
        with config_file.open('w') as _file:
            _file.write(NETWORKS_YML_2)

        # Load the config and make sure it worked
        assert yml.load_configuration(config_file) is None
        assert yml.config is not None
        assert yml.networks != []
        assert len(yml.networks) == 5

        # Make sure each netowrk exists
        assert yml.network_config_exists('test')
        assert yml.network_config_exists('dev')
        assert yml.network_config_exists('geth')
        assert yml.network_config_exists('infura-mainnet')
        assert yml.network_config_exists('infura-mainnet-http')

        # Check autodeploy_allowed
        assert yml.autodeploy_allowed('test')
        assert yml.autodeploy_allowed('dev')
        assert not yml.autodeploy_allowed('geth')
        assert not yml.autodeploy_allowed('infura-mainnet')
        assert not yml.autodeploy_allowed('infura-mainnet-http')


def test_networksyml_bytesname(mock_project):
    """ Make sure the config is loaded and it's what we expect """

    with mock_project() as mock:
        yml = NetworksYML(project_dir=mock.paths.project)

        # Make sure the test network exists
        assert yml.network_config_exists(NETWORK_NAME)

        name = mock.paths.networksyml
        bytes_name = str(name).encode('utf-8')
        yml.load_configuration(bytes_name)

        assert yml.config_file == name


def test_networksyml_invalidname(mock_project):
    """ Attempts to load a config that doesn't exist should do nothing """

    with mock_project() as mock:
        yml = NetworksYML(project_dir=mock.paths.project)

        orig_config = copy.deepcopy(yml.config)

        invalid_name = mock.paths.project.joinpath('nota.yml')

        yml.load_configuration(invalid_name)
        assert yml.config == orig_config, (
            "attempt to load file that doesn't exist should not change config"
        )


def test_networksyml_noconfig(mock_project):

    with mock_project() as mock:
        yml = NetworksYML(project_dir=mock.paths.project)

        noconfig_name = mock.paths.project.joinpath('noconfig.yml')

        with noconfig_name.open('w') as _file:
            _file.write(NETWORKS_YML_NOCONFIG)

        try:
            yml.load_configuration(noconfig_name)
            assert False, "load of a yaml file with no config should fail"
        except ConfigurationError:
            pass


def test_networksyml_network_config_noexist(mock_project):
    with mock_project() as mock:
        yml = NetworksYML(project_dir=mock.paths.project)

        # Veify with a real network
        assert yml.network_config_exists(NETWORK_NAME) is True
        assert yml.is_eth_tester(NETWORK_NAME) is True

        # Now test all with a non-existant network
        assert yml.network_config_exists('nowayiexist') is False

        try:
            yml.get_network_config('nowayiexist')
            assert False, "get_network_config() should fail on non-existant network"
        except ConfigurationError:
            pass

        try:
            yml.autodeploy_allowed('nowayiexist')
            assert False, "autodeploy_allowed() should fail on non-existant network"
        except ConfigurationError:
            pass

        try:
            yml.is_eth_tester('nowayiexist')
            assert False, "is_eth_tester() should fail on non-existant network"
        except ConfigurationError:
            pass


def test_networksyml_no_network(mock_project):
    yml = NetworksYML()
    try:
        yml.get_network_config('whatever')
        assert False, "get_network_config() should fail with no config"
    except ConfigurationError:
        pass
