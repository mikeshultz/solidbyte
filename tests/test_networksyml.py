from solidbyte.common.networks import NetworksYML
from .const import NETWORK_NAME, NETWORKS_YML_2


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
