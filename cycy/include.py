import errno
import os

from characteristic import Attribute, attributes
from rpython.rlib.streamio import open_file_as_stream

from cycy.exceptions import CyCyError


class NotFound(CyCyError):
    def __init__(self, path, searched=None):
        self.path = path
        self.searched = searched

    def __str__(self):
        return "Could not locate '%s'.\nSearched in: %s" % (
            self.path, self.searched,
        )


@attributes(
    [Attribute(name="tokens")],
    apply_with_init=False,
)
class Included(object):
    def __init__(self, tokens=None):
        if tokens is None:
            tokens = []
        self.tokens = tokens


class _Includer(object):
    pass


@attributes([Attribute(name="path")], apply_with_init=False)
class DirectoryIncluder(_Includer):
    def __init__(self, path):
        self.path = os.path.abspath(os.path.normpath(path))

    def include(self, name, parser):
        try:
            stream = open_file_as_stream(os.path.join(self.path, name))
        except OSError as error:
            if error.errno != errno.ENOENT:
                raise
            raise NotFound(path=name)
        else:
            # TODO: Probably can get lex to not take the whole str
            return Included(tokens=parser.lexer.lex(stream.readall()))


@attributes(
    [
        Attribute(name="libraries", exclude_from_repr=True)
    ],
    apply_with_init=False,
)
class StandardLibraryIncluder(_Includer):
    def __init__(self, libraries=None):
        if libraries is None:
            libraries = {
            }
        self.libraries = libraries

    def include(self, name, parser):
        library = self.libraries.get(name, None)
        if library is None:
            raise NotFound(path=name)
        return library
