from characteristic import Attribute, attributes


@attributes([Attribute(name="include_paths")], apply_with_init=False)
class Environment:
    """
    The environment we're running our interpreter in. Has a list of the
    include paths.
    """
    def __init__(self, include_paths=None):
        if include_paths is None:
            include_paths = []
        self.include_paths = include_paths

    def add_include(self, path):
        self.include_paths.append(path)
