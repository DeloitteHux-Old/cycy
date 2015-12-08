from characteristic import Attribute, attributes

from cycy import include


@attributes([Attribute(name="includers")], apply_with_init=False)
class Environment(object):
    """
    The environment we're running our interpreter in.

    """

    def __init__(self, includers=None):
        if includers is None:
            includers = []
        self.includers = includers + [include.StandardLibraryIncluder()]

    def include(self, name, parser):
        for includer in self.includers:
            try:
                return includer.include(name=name, parser=parser)
            except include.NotFound:
                pass
        raise include.NotFound(path=name, searched=self.includers)


def with_directories(directories):
    return Environment(
        includers=[
            include.DirectoryIncluder(path=directory)
            for directory in directories
        ],
    )
