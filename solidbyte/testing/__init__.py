import pytest



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
        return PlainObject({
            'ERC20': 'whatever'
        })

def run_tests():
    """ Run all tests on project """
    pytest.main([], plugins=[SolidbyteTestPlugin()])