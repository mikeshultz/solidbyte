import pytest
from attrdict import AttrDict
from ..deploy import Deployer, get_latest_from_deployed
from ..common.web3 import web3c
from ..common.exceptions import SolidbyteException


class SolidbyteTestPlugin(object):

    def __init__(self, network_name, web3=None, project_dir=None, contract_dir=None,
                 deploy_dir=None):
        self.network = network_name
        self._web3 = None
        if web3 is not None:
            self._web3 = web3

        self._project_dir = project_dir
        self._contract_dir = contract_dir
        self._deploy_dir = deploy_dir

    def pytest_sessionfinish(self):
        # TODO: There was something I wanted to do here...
        pass

    @pytest.fixture
    def contracts(self):
        if not self._web3:
            self._web3 = web3c.get_web3(self.network)
        network_id = self._web3.net.chainId or self._web3.net.version
        d = Deployer(self.network, project_dir=self._project_dir, contract_dir=self._contract_dir,
                     deploy_dir=self._deploy_dir)
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
                test_contracts[meta['name']] = self._web3.eth.contract(
                    abi=abi,
                    address=latest['address']
                )
        if len(test_contracts) == 0:
            raise SolidbyteException("No deployed contracts to test")
        return AttrDict(test_contracts)

    @pytest.fixture
    def web3(self):
        if not self._web3:
            self._web3 = web3c.get_web3(self.network)
        return self._web3


def run_tests(network_name, args=[], web3=None, project_dir=None, contract_dir=None,
              deploy_dir=None):
    """ Run all tests on project """
    return pytest.main(args, plugins=[
            SolidbyteTestPlugin(
                network_name=network_name,
                web3=web3,
                project_dir=project_dir,
                contract_dir=contract_dir,
                deploy_dir=deploy_dir,
            )
        ])
