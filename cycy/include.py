import errno
import os

from characteristic import Attribute, attributes
from rpython.rlib.streamio import open_file_as_stream

from cycy.exceptions import CyCyError
from cycy.stdlib import stdio


class NotFound(CyCyError):
    def __init__(self, path, searched=None):
        self.path = path
        self.searched = searched

    def __str__(self):
        return "Could not locate '%s'.\nSearched in: %s" % (
            self.path, self.searched,
        )


@attributes([Attribute(name="path")], apply_with_init=False)
class DirectoryIncluder(object):
    def __init__(self, path):
        self.path = os.path.abspath(os.path.normpath(path))

    def include(self, name):
        try:
            return open_file_as_stream(os.path.join(self.path, name))
        except OSError as error:
            if error.errno != errno.ENOENT:
                raise
            raise NotFound(path=name)


@attributes(
    [
        Attribute(name="libraries", exclude_from_repr=True)
    ],
    apply_with_init=False,
)
class StandardLibraryIncluder(object):
    def __init__(self, libraries=None):
        if libraries is None:
            libraries = {
                "stdio.h" : stdio,
            }
        self.libraries = libraries

    def include(self, name):
        library = self.libraries.get(name)
        if library is None:
            raise NotFound(path=name)
        return library
