from characteristic import Attribute, attributes

from cycy import include


@attributes(
    [
        Attribute(name="includers")
    ],
    apply_with_init=False,
)
class Preprocessor(object):
    def __init__(self, includers=None):
        if includers is None:
            includers = []
        self.includers = includers + [include.StandardLibraryIncluder()]

    def preprocessed(self, tokens, parser):
        """
        Preprocess a stream of tokens.

        """

        for token in tokens:
            if token.name == "INCLUDE":
                assert False  # XXX: Can't see how to translate the generator
                name = next(tokens).value[1:-1]
                included = self.environment.include(name=name, parser=parser)
                for token in included.tokens():
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
