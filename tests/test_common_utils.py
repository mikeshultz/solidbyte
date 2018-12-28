""" Test common utility functions """
from os import getcwd
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
from .utils import TMP_DIR


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


def test_supported_extension():
    assert supported_extension('MyContract.sol')


def test_source_filename_to_name():
    name = source_filename_to_name('MyContract.sol')
    assert name == 'MyContract'


def test_collapse_oel():
    assert 'one' == collapse_oel(['one'])


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


def test_defs_not_in():
    tdict = {
        'one': 1,
        'two': 2,
    }
    assert defs_not_in([('one', '-'), ('two', '-'), ('three', '-')], tdict) == ['three']
