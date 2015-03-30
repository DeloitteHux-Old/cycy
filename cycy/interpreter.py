import os

from characteristic import Attribute, attributes

from cycy import bytecode, compiler
from cycy.environment import Environment
from cycy.exceptions import CyCyError
from cycy.objects import W_Bool, W_Char, W_Int32, W_String
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


def get_location(pc, stack, variables):
    return "%s %s" % (pc, stack, variables)


jitdriver = JitDriver(
    greens=["pc", "stack", "variables"],
    reds=["byte_code", "arguments", "interpreter"],
    get_printable_location=get_location
)


@attributes(
    [
        Attribute(name="environment"),
        Attribute(name="compiled_functions"),
    ],
    apply_with_init=False
)
class CyCy(object):
    """
    The main CyCy interpreter.
    """

    def __init__(self, environment=None, handle_error=None):
        if environment is None:
            environment = Environment()

        if handle_error is None:
            def handle_error(error):
                os.write(2, str(error))
                os.write(2, "\n")

        self._handle_error = handle_error
        self.environment = environment

        self.compiled_functions = {}

    def run_main(self):
        main_byte_code = self.compiled_functions["main"]
        return self.run(main_byte_code)

    def run(self, byte_code, arguments=[]):
        pc = 0
        stack = []
        variables = [None] * len(byte_code.variables)

        assert len(byte_code.arguments) == len(arguments)
        for i in xrange(len(byte_code.arguments)):
            name = byte_code.arguments[i]
            index = byte_code.variables[name]
            variables[index] = arguments[i]

        while pc < len(byte_code.instructions):
            jitdriver.jit_merge_point(
                pc=pc,
                stack=stack,
                variables=variables,
                byte_code=byte_code,
                arguments=arguments,
                interpreter=self,
            )

            opcode = byte_code.instructions[pc]
            arg = byte_code.instructions[pc + 1]
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
                func = byte_code.constants[arg]
                args = []
                for _ in xrange(func.num_args):
                    args.append(stack.pop())
                func_byte_code = self.compiled_functions[func.name]
                rv = self.run(func_byte_code, args)
                if rv is not None:
                    stack.append(rv)
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

    def compile(self, source):
        program = parse(source=source, environment=self.environment)
        assert isinstance(program, ast.Program)

        newly_compiled_functions = []

        for function in program.functions():
            assert isinstance(function, ast.Function)
            byte_code = compiler.compile(function)
            newly_compiled_functions.append(function.name)
            self.compiled_functions[function.name] = byte_code

        return newly_compiled_functions

    def interpret(self, sources):
        for source in sources:
            try:
                self.compile(source)
            except CyCyError as error:
                self._handle_error(error)
                return

        return_value = self.run_main()
        assert isinstance(return_value, W_Int32)
        return return_value
