from characteristic import Attribute, attributes


@attributes(
    [
        Attribute(name="environment")
    ],
    apply_with_init=False,
)
class Preprocessor(object):
    def __init__(self, environment):
        self.environment = environment

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
