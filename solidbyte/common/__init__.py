from os import path, getcwd, mkdir

BUILDDIR_NAME = 'build'

def builddir(loc=None):
    """ Get (and create if necessary) the temporary build dir """
    if loc is None:
        loc = getcwd()
    full_path = path.join(loc, BUILDDIR_NAME)
    if not path.exists(full_path):
        mkdir(full_path)
    elif not path.isdir(full_path) and path.exists(full_path):
        raise FileExistsError("{} exists and is blocking the build directory creation!".format(full_path))
    return full_path

def source_filename_to_name(filename):
    """ Change a source filename to a plain name """
    if filename[-4:] != '.sol':
        raise ValueError("Invalid source filename")
    return filename[:-4]
