import pytest
from attrdict import AttrDict
from ..deploy import Deployer, get_latest_from_deployed
from ..common.web3 import web3c
from ..common.exceptions import SolidbyteException


class SolidbyteTestPlugin(object):

    def __init__(self, network_name):
        self.network = network_name

    def pytest_sessionfinish(self):
        # TODO: There was something I wanted to do here...
        pass

    @pytest.fixture
    def contracts(self):
        web3 = web3c.get_web3(self.network)
        network_id = web3.net.chainId or web3.net.version
        d = Deployer(self.network)
        contracts_meta = d.deployed_contracts
        contracts_compiled = d.source_contracts
        test_contracts = {}
        for meta in contracts_meta:
            latest = None
            if meta['networks'].get(network_id):
                latest = get_latest_from_deployed(
                    meta['networks'][network_id].get('deployedInstances'),
                    meta['networks'][network_id].get('deployedHash')
                    )
            if latest is not None:
                abi = contracts_compiled[meta['name']].abi
                test_contracts[meta['name']] = web3.eth.contract(abi=abi, address=latest['address'])
        if len(test_contracts) == 0:
            raise SolidbyteException("No deployed contracts to test")
        return AttrDict(test_contracts)

    @pytest.fixture
    def web3(self):
        web3 = web3c.get_web3(self.network)
        return web3


def run_tests(network_name):
    """ Run all tests on project """
    pytest.main([], plugins=[SolidbyteTestPlugin(network_name=network_name)])
