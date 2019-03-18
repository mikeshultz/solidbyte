from solidbyte.common.web3 import Web3ConfiguredConnection
from solidbyte.common.exceptions import SolidbyteException
from .const import NETWORKS_YML_2


def test_web3_configured_connection(temp_dir):
    with temp_dir():
        # No config, but shouldn't error immediately
        conn = Web3ConfiguredConnection()

        # Test initializing without a type
        try:
            conn._init_provider_from_type({})
            assert False, "_init_provider_from_type() should faile with no type"
        except SolidbyteException:
            pass

        # Test initializing with an invalid type
        try:
            conn._init_provider_from_type({'type': 'notatype'})
            assert False, "_init_provider_from_type() should faile with no type"
        except SolidbyteException:
            pass

        # Test initializing with an invalid type
        try:
            conn._init_provider_from_type({'type': 'notatype'})
            assert False, "_init_provider_from_type() should faile with no type"
        except SolidbyteException:
            pass

        # Test trying to get a web3 instance without config
        try:
            conn.get_web3('notanetwork')
            assert False, "get_web3() should fail with no config"
        except SolidbyteException:
            pass

        # Test getting an eth_tester web3 instance without config
        conn.get_web3('test')


def test_web3_configured_connection_with_project(mock_project):
    with mock_project() as mock:
        # No config, but shouldn't error immediately
        conn = Web3ConfiguredConnection()

        # Use the standard config for this test
        with mock.paths.networksyml.open('w') as _file:
            _file.write(NETWORKS_YML_2)

        conn._load_configuration(mock.paths.networksyml)

        """
        NOTE
        ----
        This will fail on machines that have nodes running.  It's a really bad idea to run any
        nodes on a machine you're testing on.
        """

        # If isConnected fails, get_web3 should
        try:
            conn.get_web3('geth')
            assert False, "geth should not be running or connectable"
        except SolidbyteException as err:
            assert 'Unable to connect' in str(err)

        try:
            conn.get_web3('dev')
            assert False, "auto should not work unless there's nodes running in expected places"
        except SolidbyteException as err:
            assert 'Unable to connect' in str(err)
