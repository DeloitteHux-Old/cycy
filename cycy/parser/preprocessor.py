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

        # NOTE: Can't get this to translate as a generator function.
        preprocessed = []
        for token in tokens:
            if token.name == "INCLUDE":
                literal = next(tokens)
                assert isinstance(literal, str) and len(literal) > 2
                name = literal[1:-1]
                for token in self.include(name=name, parser=parser).tokens():
                    preprocessed.append(token)
            else:
                preprocessed.append(token)
        return iter(preprocessed)

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
