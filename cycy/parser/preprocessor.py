from characteristic import Attribute, attributes

from cycy import include


@attributes(
    [Attribute(name="tokens")],
    apply_with_init=False,
)
class Included(object):
    def __init__(self, tokens=None):
        if tokens is None:
            tokens = []
        self.tokens = tokens


@attributes(
    [Attribute(name="includers")],
    apply_with_init=False,
)
class Preprocessor(object):
    def __init__(self, includers=None):
        if includers is None:
            includers = []
        self.includers = includers + _DEFAULT_INCLUDE

    def preprocessed(self, tokens, parser):
        """
        Preprocess a stream of tokens.

        """

        for token in tokens:
            if token.name == "INCLUDE":
                name = tokens.next()
                included = self.include(name=name, parser=parser)
                for token in included.tokens:
                    yield token
            else:
                yield token

    def include(self, name, parser):
        for includer in self.includers:
            try:
                return includer.include(name=name, parser=parser)
            except include.NotFound:
                pass
        raise include.NotFound(path=name, searched=self.includers)


def with_directories(directories):
    return Preprocessor(
        includers=[
            include.DirectoryIncluder(path=directory)
            for directory in directories
        ],
    )


_DEFAULT_INCLUDE = [
    include.DirectoryIncluder(path="/usr/local/include/"),
    include.DirectoryIncluder(path="/usr/include/"),
]
