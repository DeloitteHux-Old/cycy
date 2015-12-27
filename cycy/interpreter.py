import os

from characteristic import Attribute, attributes
from rpython.rlib import streamio

from cycy import bytecode
from cycy.compiler import Compiler
from cycy.exceptions import CyCyError
from cycy.objects import W_Bool, W_Char, W_Function, W_Int32, W_String
from cycy.parser.core import Parser
from cycy.parser.preprocessor import Preprocessor

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


def get_location(pc, stack, variables):
    return "%s %s" % (pc, stack, variables)


jitdriver = JitDriver(
    greens=["pc", "stack", "variables"],
    reds=["byte_code", "arguments", "interpreter"],
    get_printable_location=get_location
)


@attributes(
    [
        Attribute(name="compiler"),
        Attribute(name="parser"),
        Attribute(name="functions", exclude_from_repr=True),
    ],
    apply_with_init=False,
)
class CyCy(object):
    """
    The main CyCy interpreter.

    """

    def __init__(
        self,
        compiler=None,
        parser=None,
        functions=None,
        stdin=None,
        stdout=None,
        stderr=None,
        handle_error=None,
    ):
        if compiler is None:
            compiler = Compiler()
        if parser is None:
            parser = Parser(preprocessor=Preprocessor())
        if functions is None:
            functions = {}
        if handle_error is None:
            handle_error = self._show_traceback

        self._handle_error = handle_error
        self.compiler = compiler
        self.parser = parser
        self.functions = functions

        # NOTE: This uses streamio, which by its own admission "isn't
        #       ready for general usage"
        self.stdin = stdin if stdin is not None else _open(fd=0)
        self.stdout = stdout if stdout is not None else _open(fd=1)
        self.stderr = stderr if stderr is not None else _open(fd=2)

    def run(self, byte_code, arguments=[]):
        pc = 0
        stack = []
        variables = [None] * len(byte_code.variables)

        assert len(byte_code.arguments) == len(arguments)
        for i in xrange(len(byte_code.arguments)):
            name = byte_code.arguments[i]
            index = byte_code.variables[name]
            variables[index] = arguments[i]

        while pc < len(byte_code.tape):
            jitdriver.jit_merge_point(
                pc=pc,
                stack=stack,
                variables=variables,
                byte_code=byte_code,
                arguments=arguments,
                interpreter=self,
            )

            opcode = byte_code.tape[pc]
            arg = byte_code.tape[pc + 1]
            pc += 2

            if opcode == bytecode.LOAD_CONST:
                value = byte_code.constants[arg]
                stack.append(value)
            elif opcode == bytecode.BINARY_NEQ:
                left = stack.pop()
                right = stack.pop()
                assert isinstance(left, W_Int32) or isinstance(left, W_Char)
                assert isinstance(right, W_Int32)
                stack.append(W_Bool(left.neq(right)))
            elif opcode == bytecode.PUTC:
                value = stack.pop()
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
                w_func = byte_code.constants[arg]

                args = []
                for _ in xrange(w_func.arity):
                    args.append(stack.pop())

                return_value = w_func.call(arguments=args, interpreter=self)
                if return_value is not None:
                    stack.append(return_value)
            elif opcode == bytecode.RETURN:
                if arg == 1:
                    return stack.pop()
                else:
                    return None
            elif opcode == bytecode.STORE_VARIABLE:
                val = stack.pop()
                variables[arg] = val
            elif opcode == bytecode.LOAD_VARIABLE:
                stack.append(variables[arg])
            elif opcode == bytecode.BINARY_ADD:
                left = stack.pop()
                right = stack.pop()
                assert isinstance(left, W_Int32)
                assert isinstance(right, W_Int32)
                stack.append(W_Int32(left.add(right)))
            elif opcode == bytecode.BINARY_SUB:
                left = stack.pop()
                right = stack.pop()
                assert isinstance(left, W_Int32)
                assert isinstance(right, W_Int32)
                stack.append(W_Int32(left.sub(right)))
            elif opcode == bytecode.DEREFERENCE:
                array = stack.pop()
                index = stack.pop()
                assert isinstance(array, W_String)
                assert isinstance(index, W_Int32)
                stack.append(W_Char(array.dereference(index)))
            elif opcode == bytecode.JUMP:
                old_pc = pc
                pc = arg
                if pc < old_pc:
                    # If we're jumping backwards, we're entering a loop
                    # so we can probably enter the jit
                    jitdriver.can_enter_jit(
                        pc=pc,
                        stack=stack,
                        variables=variables,
                        byte_code=byte_code,
                        arguments=arguments,
                        interpreter=self,
                    )
            elif opcode == bytecode.JUMP_IF_NOT_ZERO:
                val = stack.pop()
                if val.is_true():
                    pc = arg
            elif opcode == bytecode.JUMP_IF_ZERO:
                val = stack.pop()
                if not val.is_true():
                    pc = arg

        assert False, "bytecode exited the main loop without returning"

    def interpret(self, sources):
        for source in sources:
            try:
                program = self.parser.parse(source=source)
                if program is None:
                    return
                self.compiler.compile(program)
            except CyCyError as error:
                if self._handle_error(error) is None:
                    return
                raise

            w_main = self.compiler.constants[self.compiler.functions["main"]]
            return_value = w_main.call(arguments=[], interpreter=self)
            assert isinstance(return_value, W_Int32)
            return return_value

    def _show_traceback(self, error):
        self.stdout.write(error.rstr())
        self.stdout.write("\n")


def _open(fd):
    base = streamio.DiskFile(fd)
    return streamio.BufferingInputStream(base)
