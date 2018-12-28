from os import path, getcwd, mkdir

BUILDDIR_NAME = 'build'
SUPPORTED_EXTENSIONS = ('sol',)


def builddir(loc=None):
    """ Get (and create if necessary) the temporary build dir """
    if loc is None:
        loc = getcwd()
    full_path = path.join(loc, BUILDDIR_NAME)
    if not path.exists(full_path):
        mkdir(full_path)
    elif not path.isdir(full_path) and path.exists(full_path):
        raise FileExistsError("{} exists and is blocking the build directory creation!".format(
                full_path
            ))
    return full_path


def get_filename_and_ext(filename):
    """ Return the filename extension """
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
