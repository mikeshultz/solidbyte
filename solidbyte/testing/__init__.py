import pytest
from ..deploy import Contracts, get_latest_from_deployed
from ..common.web3 import web3

class PlainObject(object):
    def __init__(self, attr_dict):
        super(PlainObject, self).__setattr__('_dict', attr_dict)

    def __getattr__(self, key):
        return self._dict[key]

    def __setattr__(self, key, val):
        self._dict[key] = val

class SolidbyteTestPlugin(object):
    def pytest_sessionfinish(self):
        print("*** test run reporting finishing")

    @pytest.fixture
    def contracts(self):
        c = Contracts()
        contracts_meta = c.get_deployed_contracts()
        contracts_compiled = c.get_contracts()
        test_contracts = {}
        for meta in contracts_meta:
            latest = get_latest_from_deployed(meta['deployedInstances'], meta['deployedHash'])
            # TODO: This is a fucky API here, why is that tuples?
            abi = contracts_compiled[meta['name']][0]
            test_contracts[meta['name']] = web3.eth.contract(abi=abi, address=latest['address'])
        return PlainObject(test_contracts)

    @pytest.fixture
    def web3(self):
        return web3

def run_tests():
    """ Run all tests on project """
    pytest.main([], plugins=[SolidbyteTestPlugin()])