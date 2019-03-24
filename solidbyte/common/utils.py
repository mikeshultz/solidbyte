import hashlib
from typing import Iterable
from shutil import which
from pathlib import Path
from datetime import datetime as datetime

BUILDDIR_NAME = 'build'
SUPPORTED_EXTENSIONS = ('sol', 'vy')
JS_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class Py36Datetime(datetime):
    """ Monkeypatch datetime for python<3.7 """
    def fromisoformat(s):
        """ Load an :code:`datetime.isoformat()` date string as a :code:`datetime` object """
        return datetime.strptime(s, JS_DATE_FORMAT)


def builddir(loc=None):
    """ Get (and create if necessary) the temporary build dir

    :param loc: (:class:`pathlib.Path`) to workdir (default: pwd)
    :returns: (:class:`pathlib.Path`) to build dir
    """
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
    """ Return the filename and extension as a tuple

    :param filename: (:class:`pathlib.Path`) of file
    :returns: (:code:`tuple`) of (name, extension)
    """
    if isinstance(filename, Path):
        filename = filename.name
    cmps = filename.split('.')
    if len(cmps) < 2:
        return (filename, '')
    ext = cmps.pop()
    return ('.'.join(cmps), ext)


def supported_extension(filename):
    """ Check if the provided filename has a supported source code extension

    :param filename: (:class:`pathlib.Path`) of file
    :returns: (:code:`bool`) if it's supported
    """
    _, ext = get_filename_and_ext(filename)
    if ext in SUPPORTED_EXTENSIONS:
        return True
    return False


def source_filename_to_name(filename):
    """ Change a source filename to a plain name

    :param filename: (:class:`pathlib.Path`) of file
    :returns: (:code:`str`) name of file without extension
    """
    if not supported_extension(filename):
        raise ValueError("Invalid source filename")
    name, _ = get_filename_and_ext(filename)
    return name


def collapse_oel(lst):
    """ Collapse a one-element list to a single var

    :param filename: (:code:`list`) with one element to collapse
    :returns: (:code:`Any`) the single element
    """
    if type(lst) != list:
        raise ValueError("Not a list")
    if len(lst) != 1:
        raise ValueError("List has multiple elements")
    return lst[0]


def pop_key_from_dict(d, key):
    """ Remove and return an element from a dict and the modded dict without throwing an exception
    if a key does not exist.

    :param d: (:code:`dict`) the original dict
    :param key: (:code:`str`) they key to pop

    :returns: (:code:`T`) The value of the key or None
    """
    if key not in d:
        return None
    val = d.get(key)
    del d[key]
    return val


def all_defs_in(items: Iterable, di: dict) -> bool:
    """ Check if all defs(tuple of name/placeholder) are in di

    :param items: (:code:`Iterable`) to check against di
    :param di: (:code:`dict`) the dict to check against
    :returns: (:code:`bool`) if all defs are in the dict
    """
    for i in items:
        if i[0] not in di:
            return False
    return True


def defs_not_in(items: Iterable, di: dict) -> set:
    """ Find defs (tuple of name/placeholder) that aren't keys in a dict

    :param items: (:code:`Iterable`) to check against di
    :param di: (:code:`dict`) the dict to check against
    :returns: (:code:`set`) any defs not in di
    """
    missing_items = set()
    for i in items:
        if i[0] not in di:
            missing_items.add(i[0])
    return missing_items


def find_vyper():
    """ Get the path to vyper. **DEPRECIATED** """
    return which('vyper')


def hash_file(_file: Path) -> str:
    """ Get an sha1 hash of a file

    :param _file: (:class:`pathlib.Path`) the file to hash
    :returns: (:code:`str`) hex sha1 hash of the given file
    """

    if not _file or not isinstance(_file, Path) or not _file.is_file():
        raise ValueError("Invalid _file given to hash_file()")

    CHUNK_SIZE = 65536

    _hash = hashlib.sha1()
    with _file.open() as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            _hash.update(chunk.encode('utf-8'))
    return _hash.hexdigest()


def to_path(v) -> Path:
    """ Given a Path or str, return a Path

    :param v: (:code:`str` or :class:`pathlib.Path`)
    :returns: (:class:`pathlib.Path`)
    """
    if isinstance(v, Path):
        return v
    return Path(v).expanduser().resolve()


def to_path_or_cwd(v) -> Path:
    """ Given a Path, str, or None, return a Path of the given path or the current working directory

    :param v: (:code:`str` or :class:`pathlib.Path`)
    :returns: (:class:`pathlib.Path`)
    """
    if not v:
        return Path.cwd()
    return to_path(v)


def keys_with(thedict, term):
    """ Return any keys from :code:`thedict` that have :code:`term` in their value

    :param thedict: (:code:`dict`) The dict to search
    :param term: (:code:`Any`) The value to look for
    :returns: (:code:`list`) List of keys that match
    """
    keys = []
    for k, v in thedict.items():
        if term in v:
            keys.append(k)
    return keys


def unescape_newlines(s):
    """ Unescape newlines in a text string

    :param s: (:code:`str`) String to search and replace against
    :returns: (:code:`str`) String with unescaped newlines
    """
    if type(s) == bytes:
        s = s.decode('utf-8')
    return s.replace('\\n', '\n')
