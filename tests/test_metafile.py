import json
from solidbyte.common.metafile import MetaFile
from solidbyte.common.web3 import normalize_address
from .utils import TMP_DIR, ADDRESS_1, ADDRESS_2, NETWORK_ID, ABI_OBJ_1, BYTECODE_HASH_1


def test_metafile():
    """ Test metafile creating and writing """
    mfilename = TMP_DIR.joinpath('metafile.json')
    mfile = MetaFile(filename_override=str(mfilename))

    # Contracts
    assert mfile.get_all_contracts() == {}
    assert mfile.get_contract('FakeName') is None
    assert mfile.get_contract_index('FakeName') is None

    mfile.add('FakeName', NETWORK_ID, ADDRESS_1, ABI_OBJ_1, BYTECODE_HASH_1)
    fakeName = mfile.get_contract('FakeName')
    assert fakeName is not None
    print(fakeName)
    instances = None
    try:
        instances = fakeName['networks'][str(NETWORK_ID)]['deployedInstances']
    except KeyError:
        assert False, "Invalid deployment structure in metafile.json"
    assert instances is not None
    assert len(instances) == 1
    assert instances[0].get('hash') == BYTECODE_HASH_1
    assert instances[0].get('address') == normalize_address(ADDRESS_1)
    assert mfile.get_contract_index('FakeName') == 0

    # Accounts
    assert mfile.account_known(ADDRESS_2) is False
    assert mfile.add_account(ADDRESS_2) is None
    assert mfile.account_known(ADDRESS_2) is True
    assert mfile.get_default_account() is None
    assert mfile.set_default_account(ADDRESS_2) is None
    assert mfile.get_default_account() == normalize_address(ADDRESS_2)
