import os

from characteristic import Attribute, attributes
from rply.errors import LexingError as _RPlyLexingError

from cycy import bytecode
from cycy.compiler import Compiler
from cycy.environment import Environment
from cycy.exceptions import CyCyError
from cycy.objects import W_Bool, W_Char, W_Function, W_Int32, W_String
from cycy.parser import ast
from cycy.parser.lexer import lexer
from cycy.parser.sourceparser import PARSER
from cycy.parser.preprocessor import preprocessed

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


class NoSuchFunction(CyCyError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return repr(self.name)


jitdriver = JitDriver(
    greens=["pc", "stack", "variables"],
    reds=["byte_code", "arguments", "interpreter"],
    get_printable_location=get_location
)


@attributes(
    [
        Attribute(name="environment"),
        Attribute(name="compiler"),
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
        environment=None,
        functions=(),
        handle_error=None,
    ):
        if environment is None:
            environment = Environment()
        if compiler is None:
            compiler = Compiler()

        if handle_error is None:
            def handle_error(error):
                os.write(2, error.rstr())
                os.write(2, "\n")

        self._handle_error = handle_error
        self.compiler = compiler
        self.environment = environment
        self.functions = dict(functions)

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

                return_value = self.call(w_func, arguments=args)
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
            program = self.parse(source=source)
            assert isinstance(program, ast.Program)

            self.compiler.compile(program)
            try:
                w_main = self.compiler.constants[
                    self.compiler.functions["main"]
                ]
                return_value = self.call(w_main, arguments=[])
            except CyCyError as error:
                self._handle_error(error)
                return
            else:
                assert isinstance(return_value, W_Int32)
                return return_value

    def parse(
        self,
        source,
        lexer=lexer,
        preprocessor=preprocessed,
        parser=PARSER,
    ):
        tokens = lexer.lex(source)
        preprocessed = preprocessor(tokens=tokens, interpreter=self)

        try:
            return parser.parse(preprocessed)
        except _RPlyLexingError as error:
            raise LexingError(
                source_pos=error.source_pos,
                message=error.message,
            )

    def call(self, w_func, arguments):
        return self.run(w_func.bytecode, arguments=arguments)
