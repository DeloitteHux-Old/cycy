class Environment:
    """
    The environment we're running our interpreter in. Has a list of the
    include paths.
    """
    def __init__(self):
        self.include_paths = []

    def add_include(self, path):
        self.include_paths.append(path)
