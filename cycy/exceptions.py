class CyCyError(Exception):
    """
    Base class for non-runtime internal errors.

    """

    def rstr(self):
        return self.__str__()
