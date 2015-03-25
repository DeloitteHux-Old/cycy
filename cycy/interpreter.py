class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def run(self, bytecode):
        print "Hello, world!"

def compile(source):
    pass

def interpret(source):
    bytecode = compile(source)
    CyCy().run(bytecode)
