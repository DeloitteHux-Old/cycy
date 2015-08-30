from characteristic import Attribute, attributes


def preprocessed(tokens, interpreter):
    """
    Preprocess a stream of tokens.

    """

    for token in tokens:
        if token.name == "INCLUDE":
            name = next(tokens).value[1:-1]
            included = interpreter.environment.include(name=name)
            for token in included.tokens():
                yield token
        else:
            yield token
