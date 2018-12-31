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
)
from .const import TMP_DIR


def test_builddir():
    TMP_DIR.joinpath('builddir-test').mkdir(parents=True)
    loc = builddir(TMP_DIR.joinpath('builddir-test'))
    ploc = Path(loc)
    assert ploc.exists() and ploc.is_dir()
    build_loc = TMP_DIR.joinpath('builddir-test', 'build')
    assert build_loc.exists() and build_loc.is_dir()


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
    tdict, popped = pop_key_from_dict(tdict, 'two')
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
    assert defs_not_in([('one', '-'), ('two', '-'), ('three', '-')], tdict) == ['three']
