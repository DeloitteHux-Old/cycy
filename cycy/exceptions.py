class CyCyError(Exception):
    """
    Base class for non-runtime internal errors.

    """

    def rstr(self):
        return "%s: %s" % (self.__class__.__name__, self.__str__())
