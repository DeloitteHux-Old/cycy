import errno
import os

from characteristic import Attribute, attributes
from rpython.rlib.streamio import open_file_as_stream

from cycy.parser.preprocessor import IncludeNotFound


@attributes([Attribute(name="include_paths")], apply_with_init=False)
class Environment(object):
    """
    The environment we're running our interpreter in.

    """

    def __init__(self, include_paths=None):
        if include_paths is None:
            include_paths = []
        self.include_paths = [
            os.path.abspath(os.path.normpath(path)) for path in include_paths
        ]

    def include(self, file_path):
        for include_path in self.include_paths:
            full_path = os.path.join(include_path, file_path)
            try:
                return open_file_as_stream(full_path)
            except OSError as error:
                if error.errno != errno.ENOENT:
                    raise
        raise IncludeNotFound(path=file_path, searched=self.include_paths)
