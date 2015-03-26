import os

from cycy import bytecode, compiler
from cycy.objects import W_Char, W_Int32, W_Bool
from cycy.parser import ast
from cycy.parser.sourceparser import parse

# So that you can still run this module under standard CPython, I add this
# import guard that creates a dummy class instead.
try:
    from rpython.rlib.jit import JitDriver, purefunction
except ImportError:
    class JitDriver(object):
        def __init__(self,**kw): pass
        def jit_merge_point(self,**kw): pass
        def can_enter_jit(self,**kw): pass
    def purefunction(f): return f

def get_location(pc, stack):
    return "%s %s" % (pc, stack)

jitdriver = JitDriver(
    greens=['pc', 'stack'],
    reds=['byte_code'],
    get_printable_location=get_location,
)

class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def __init__(self):
        self.compiled_functions = {}

    def run_main(self):
        main_byte_code = self.compiled_functions["main"]
        self.run(main_byte_code)

    def run(self, byte_code):
        pc = 0
        stack = []

        while pc < len(byte_code.instructions):
            jitdriver.jit_merge_point(pc=pc, byte_code=byte_code, stack=stack)

            opcode = byte_code.instructions[pc]
            arg = byte_code.instructions[pc + 1]
            pc += 2

            if opcode == bytecode.LOAD_CONST:
                value = byte_code.constants[arg]
                stack.append(value)
            elif opcode == bytecode.BINARY_NEQ:
                left = stack.pop()
                right = stack.pop()
                assert isinstance(left, W_Int32)
                assert isinstance(right, W_Int32)
                stack.append(W_Bool(left.neq(right)))
            elif opcode == bytecode.PUTC:
                value = byte_code.constants[arg]
                assert isinstance(value, W_Char)
                os.write(1, value.char)
                # TODO: error handling?
            elif opcode == bytecode.BINARY_LEQ:
                left = stack.pop()
                right = stack.pop()
                assert isinstance(left, W_Int32)
                assert isinstance(right, W_Int32)
                stack.append(W_Bool(left.leq(right)))
            elif opcode == bytecode.CALL:
                func = byte_code.constants[arg]
                # TODO: arguments
                func_byte_code = self.compiled_functions[func.name]
                rv = self.run(func_byte_code)
                if rv is not None:
                    stack.append(rv)
            elif opcode == bytecode.RETURN:
                if arg == 1:
                    return stack.pop()
                else:
                    return None

        assert False, "bytecode exited the main loop without returning"


def interpret(source):
    interp = CyCy()
    program = parse(source)

    assert isinstance(program, ast.Program)
    for function in program.functions:
        assert isinstance(function, ast.Function)
        byte_code = compiler.compile(function)
        interp.compiled_functions[function.name] = byte_code

    rv = interp.run_main()
    assert isinstance(rv, W_Int32)
    return rv.value
