class CyCyError(Exception):
    """
    Base class for non-runtime internal errors.

    """

    def rstr(self):
        name = self.__class__.__name__
        return "%s\n%s\n\n%s" % (name, "-" * len(name), self.__str__())
