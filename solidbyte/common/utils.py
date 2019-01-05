import hashlib
from shutil import which
from pathlib import Path

BUILDDIR_NAME = 'build'
SUPPORTED_EXTENSIONS = ('sol', 'vy')


def builddir(loc=None):
    """ Get (and create if necessary) the temporary build dir """
    if loc is None:
        loc = Path.cwd()
    full_path = Path(loc, BUILDDIR_NAME)
    if not full_path.exists():
        full_path.mkdir()
    elif not full_path.is_dir():
        raise FileExistsError("{} exists and is blocking the build directory creation!".format(
                full_path
            ))
    return full_path


def get_filename_and_ext(filename):
    """ Return the filename and extension as a tuple """
    if isinstance(filename, Path):
        filename = filename.name
    cmps = filename.split('.')
    if len(cmps) < 2:
        return (filename, '')
    ext = cmps.pop()
    return ('.'.join(cmps), ext)


def supported_extension(filename):
    """ Check if the provided filename has a supported extension """
    _, ext = get_filename_and_ext(filename)
    if ext in SUPPORTED_EXTENSIONS:
        return True
    return False


def source_filename_to_name(filename):
    """ Change a source filename to a plain name """
    if not supported_extension(filename):
        raise ValueError("Invalid source filename")
    name, _ = get_filename_and_ext(filename)
    return name


def collapse_oel(lst):
    """ Collapse a one-element list to a single var """
    if type(lst) != list:
        raise ValueError("Not a list")
    if len(lst) != 1:
        raise ValueError("List has multiple elements")
    return lst[0]


def pop_key_from_dict(d, key):
    """ Remove and return an element from a dict and the modded dict

    Args:
        d {dict}: the original dict
        key {str}: they key to pop

    Returns:
        {tuple}: A tuple of a dict and the wanted value
    """
    val = d.get(key)
    if val is None:
        return (d, None)
    del d[key]
    return (d, val)


def all_defs_in(items: list, di: dict):
    """ Check if all defs(tuple of name/placeholder) are in di """
    for i in items:
        if i[0] not in di:
            return False
    return True


def defs_not_in(items: list, di: dict):
    """ Find items tha taren't keys in a dict """
    missing_items = []
    for i in items:
        if i[0] not in di:
            missing_items.append(i[0])
    return missing_items


def find_vyper():
    """ Get the path to vyper """
    return which('vyper')


def hash_file(_file: Path) -> bytes:
    """ Get an sha1 hash for a file """

    if not _file or not isinstance(_file, Path) or not _file.is_file():
        raise ValueError("Invalid _file given to hash_file()")

    CHUNK_SIZE = 65536

    _hash = hashlib.sha1()
    with _file.open() as _file:
        while True:
            chunk = _file.read(CHUNK_SIZE)
            if not chunk:
                break
            _hash.update(chunk.encode('utf-8'))
    return _hash.hexdigest()


def to_path(v) -> Path:
    if isinstance(v, Path):
        return v
    return Path(v).expanduser().resolve()


def to_path_or_cwd(v) -> Path:
    if not v:
        return Path.cwd()
    return to_path(v)
