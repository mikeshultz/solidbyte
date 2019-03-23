from datetime import datetime
from solidbyte.common.metafile import MetaFile
from solidbyte.common.web3 import normalize_address
from solidbyte.common.utils import hash_file
from .const import TMP_DIR, ADDRESS_1, ADDRESS_2, NETWORK_ID, ABI_OBJ_1, BYTECODE_HASH_1


def test_metafile():
    """ Test metafile creating and writing """
    if not TMP_DIR.exists():
        TMP_DIR.mkdir()
    mfilename = TMP_DIR.joinpath('metafile.json')
    mfile = MetaFile(filename_override=str(mfilename))

    # Contracts
    assert mfile.get_all_contracts() == []
    assert mfile.get_contract('FakeName') is None
    assert mfile.get_contract_index('FakeName') == -1

    mfile.add('FakeName', NETWORK_ID, ADDRESS_1, ABI_OBJ_1, BYTECODE_HASH_1)
    fakeName = mfile.get_contract('FakeName')
    assert fakeName is not None

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

    mfile2 = MetaFile(filename_override=str(mfilename))
    assert mfile2.get_default_account() == mfile.get_default_account()


def test_metafile_cleanup(mock_project):
    """ Test the cleanup method of MetaFile. """

    CONTRACT_NAME_1 = 'PhantomContract'
    NETWORK_ID_1 = 15  # Won't be cleaned up
    NETWORK_ID_2 = 101
    NETWORK_ID_3 = int(datetime.now().timestamp())

    with mock_project() as mock:
        project_dir = mock.paths.project

        mfile = MetaFile(project_dir=project_dir)

        # Make sure this is an unused name because I'm feeling defensive
        assert mfile.get_contract_index(CONTRACT_NAME_1) == -1

        # Add the instances
        assert mfile.add(CONTRACT_NAME_1, NETWORK_ID_1, ADDRESS_1, {}, BYTECODE_HASH_1) is None
        assert mfile.get_contract_index(CONTRACT_NAME_1) > -1
        assert mfile.add(CONTRACT_NAME_1, NETWORK_ID_2, ADDRESS_1, {}, BYTECODE_HASH_1) is None
        assert mfile.add(CONTRACT_NAME_1, NETWORK_ID_3, ADDRESS_1, {}, BYTECODE_HASH_1) is None

        c_entry = mfile.get_contract(CONTRACT_NAME_1)
        assert c_entry is not None
        assert c_entry['name'] == CONTRACT_NAME_1
        assert len(c_entry['networks']) == 3

        # Now attempt cleanup
        assert mfile.cleanup()

        # Should still have one entry
        assert mfile.get_contract_index(CONTRACT_NAME_1) > -1
        d_entry = mfile.get_contract(CONTRACT_NAME_1)
        assert len(d_entry['networks']) == 1

        reloaded_mfile = MetaFile(project_dir=project_dir)

        # Get an entirely new instance so we know the file was updated
        assert reloaded_mfile.get_contract_index(CONTRACT_NAME_1) > -1
        e_entry = reloaded_mfile.get_contract(CONTRACT_NAME_1)
        assert len(e_entry['networks']) == 1


def test_metafile_backup(mock_project):
    """ Test backup method of MetaFile """

    CONTRACT_NAME_1 = 'PhantomContract'
    NETWORK_ID_1 = 15

    with mock_project() as mock:
        project_dir = mock.paths.project
        mfilename = 'metafile.json'
        metafile_path = project_dir.joinpath(mfilename)
        outfile = project_dir.joinpath('metafile.json.bak')
        mfile = MetaFile(filename_override=mfilename, project_dir=project_dir)

        # Add one so we have something in the file
        assert mfile.add(CONTRACT_NAME_1, NETWORK_ID_1, ADDRESS_1, {}, BYTECODE_HASH_1) is None

        # Get the original hash of the file
        assert metafile_path.exists() and metafile_path.is_file()
        orig_hash = hash_file(metafile_path)

        # Backup
        mfile.backup(outfile)

        backup_hash = hash_file(outfile)

        assert str(metafile_path) != str(outfile)
        assert orig_hash == backup_hash


def test_metafile_read_only(mock_project):
    """ Test backup method of MetaFile """

    CONTRACT_NAME_1 = 'PhantomContract'
    NETWORK_ID_1 = 15

    with mock_project() as mock:
        project_dir = mock.paths.project
        mfile = MetaFile(project_dir=project_dir, read_only=True)

        # Add one so we have something in the file
        assert mfile.add(CONTRACT_NAME_1, NETWORK_ID_1, ADDRESS_1, {}, BYTECODE_HASH_1) is None

        # Reload the file and verify our changes don't exist
        reloaded_mfile = MetaFile(project_dir=project_dir)

        # Get an entirely new instance so we know the file was updated
        assert reloaded_mfile.get_contract_index(CONTRACT_NAME_1) == -1
        e_entry = reloaded_mfile.get_contract(CONTRACT_NAME_1)
        assert e_entry is None
