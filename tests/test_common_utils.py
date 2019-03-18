""" Test common utility functions """
from pathlib import Path
from solidbyte.common import (
    builddir,
    get_filename_and_ext,
    supported_extension,
    source_filename_to_name,
    collapse_oel,
    pop_key_from_dict,
    all_defs_in,
    defs_not_in,
    hash_file,
    keys_with,
    unescape_newlines,
)
from .const import TMP_DIR, HASHABLE_FILE, HASHABLE_FILE_HASH


def test_builddir():
    TMP_DIR.joinpath('builddir-test').mkdir(parents=True)
    loc = builddir(TMP_DIR.joinpath('builddir-test'))
    ploc = Path(loc)
    assert ploc.exists() and ploc.is_dir()
    build_loc = TMP_DIR.joinpath('builddir-test', 'build')
    assert build_loc.exists() and build_loc.is_dir()


def test_builddir_conflict():
    """ Test that it throws when a file is in the way """
    test_dirname = 'builddir-test-invalid'
    workdir = TMP_DIR.joinpath(test_dirname)
    workdir.mkdir(parents=True)
    workdir.joinpath('build').touch()
    loc = None
    try:
        loc = builddir(workdir)
        assert False, "builddir() should have thrown an exception on conflict"
    except FileExistsError:
        pass
    assert loc is None


def test_get_filename_and_ext():
    fname1, ext1 = get_filename_and_ext('whatever.txt')
    assert fname1 == 'whatever'
    assert ext1 == 'txt'
    fname2, ext2 = get_filename_and_ext('multiple.dots.dat')
    assert fname2 == 'multiple.dots'
    assert ext2 == 'dat'
    fname2, ext2 = get_filename_and_ext('nodots')
    assert fname2 == 'nodots'
    assert ext2 == ''


def test_supported_extension():
    assert supported_extension('MyContract.sol')
    assert not supported_extension('MyContract.cpp')


def test_source_filename_to_name():
    name = source_filename_to_name('MyContract.sol')
    assert name == 'MyContract'
    try:
        name = source_filename_to_name('MyContract.cpp')
        assert False, "Should have raised a ValueError"
    except ValueError:
        assert True


def test_collapse_oel():
    assert 'one' == collapse_oel(['one'])
    try:
        collapse_oel('MyContract.sol')
        assert False, "Should have raised a ValueError"
    except ValueError:
        assert True
    try:
        collapse_oel(['one', 'two'])
        assert False, "Should have raised a ValueError"
    except ValueError:
        assert True


def test_pop_key_from_dict():
    tdict = {
        'one': 1,
        'two': 2,
    }
    popped = pop_key_from_dict(tdict, 'two')
    assert len(tdict) == 1
    assert 'two' not in tdict
    assert popped == 2


def test_all_defs_in():
    tdict = {
        'one': 1,
        'two': 2,
    }
    assert all_defs_in([('one', '-'), ('two', '-')], tdict)
    assert not all_defs_in([('three', '-')], tdict)


def test_defs_not_in():
    tdict = {
        'one': 1,
        'two': 2,
    }
    assert defs_not_in([('one', '-'), ('two', '-'), ('three', '-')], tdict) == {'three'}


def test_keys_with():
    """ Test the keys_with func """
    tdict = {
        'one': 'ohhello',
        'two': 'ohhellno',
        'three': 'hello world',
    }
    keys = keys_with(tdict, 'hello')
    assert 'one' in keys
    assert 'two' not in keys
    assert 'three' in keys


def test_hash_file(temp_dir):
    """ Test the hash_file func """

    with temp_dir() as workdir:
        test_file = workdir.joinpath('hashable.file')

        # Fail if file doesn't exist
        try:
            hash_file(test_file)
            assert False, "hash_file() should have failed on a non-existent file"
        except ValueError as err:
            assert 'Invalid' in str(err)

        # Create the file
        with test_file.open('w') as _file:
            _file.write(HASHABLE_FILE)

        # Verify expected hash
        assert hash_file(test_file) == HASHABLE_FILE_HASH


def test_unescape_newlines():
    tstring = "hello\\nworld"
    tstring_unescaped = """hello
world"""

    assert unescape_newlines(tstring) == tstring_unescaped
