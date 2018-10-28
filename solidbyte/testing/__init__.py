import pytest
from attrdict import AttrDict
from ..deploy import Deployer, get_latest_from_deployed
from ..common.web3 import web3c

class SolidbyteTestPlugin(object):
    def pytest_sessionfinish(self):
        print("*** test run reporting finishing")

    @pytest.fixture
    def contracts(self):
        web3 = web3c.get_web3()
        d = Deployer()
        contracts_meta = d.deployed_contracts
        contracts_compiled = d.source_contracts
        test_contracts = {}
        for meta in contracts_meta:
            latest = get_latest_from_deployed(meta['deployedInstances'], meta['deployedHash'])
            abi = contracts_compiled[meta['name']].abi
            test_contracts[meta['name']] = web3.eth.contract(abi=abi, address=latest['address'])
        return AttrDict(test_contracts)

    @pytest.fixture
    def web3(self):
        web3 = web3c.get_web3()
        return web3

def run_tests():
    """ Run all tests on project """
    pytest.main([], plugins=[SolidbyteTestPlugin()])