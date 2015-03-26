from characteristic import Attribute, attributes

from cycy import bytecode
from cycy.objects import W_Int32
from cycy.parser import ast


@attributes(
    [
        Attribute(name="instructions"),
        Attribute(name="constants"),
        Attribute(name="variable_indices"),
    ],
    apply_with_init=False,
)
class Context(object):
    """
    The compilation context, which stores the state during interpretation.

    .. attribute:: instructions

        a :class:`list` of bytecode instructions (:class:`int`\ s)

    .. attribute:: constants

        the :class:`list` of contents that the bytecode indexes into.

        .. note::

            These are C-level objects (i.e. they're wrapped).

    .. attribute:: variable_indices

        a mapping between variable names (:class:`str`\ s) and the
        indices in an array that they should be assigned to

    """

    def __init__(self):
        self.instructions = []
        self.constants = []
        self.variable_indices = {}

    def emit(self, byte_code, arg=bytecode.NO_ARG):
        self.instructions.append(byte_code)
        self.instructions.append(arg)

    def register_int32_variable(self, name):
        self.variable_indices[name] = len(self.variable_indices)
        return len(self.variable_indices) - 1

    def register_int32_constant(self, int32):
        self.constants.append(int32)
        return len(self.constants) - 1

    def build(self, name="<input>"):
        return bytecode.Bytecode(
            instructions=self.instructions,
            name=name,
            constants=self.constants,
            number_of_variables=len(self.variable_indices),
        )

class __extend__(ast.Function):
    def compile(self, context):
        self.body.compile(context=context)

class __extend__(ast.Block):
    def compile(self, context):
        for statement in self.statements:
            statement.compile(context=context)

class __extend__(ast.BinaryOperation):
    def compile(self, context):
        self.left.compile(context=context)
        self.right.compile(context=context)
        context.emit(bytecode.BINARY_OPERATION_BYTECODE[self.operator])

class __extend__(ast.Int32):
    def compile(self, context):
        wrapped = W_Int32(value=self.value)
        index = context.register_int32_constant(wrapped)
        context.emit(bytecode.LOAD_CONST, index)

class __extend__(ast.ReturnStatement):
    def compile(self, context):
        if self.value:
            self.value.compile(context)
        context.emit(bytecode.RETURN)

class __extend__(ast.While):
    def compile(self, context):
        self.condition.compile(context)
        jump_ix = len(context.instructions)
        context.emit(bytecode.JUMP_IF_NOT_ZERO, 0)
        self.body.compile(context)
        context.emit(bytecode.JUMP, jump_ix + 2)
        context.instructions[jump_ix + 1] = len(context.instructions)

class __extend__(ast.VariableDeclaration):
    def compile(self, context):
        if self.vtype == "INT32":
            variable_index = context.register_int32_variable(self.name)
            if self.value:
                self.value.compile(context)
                context.emit(bytecode.STORE_VARIABLE, variable_index)
            # else we've declared the variable, but it is
            # uninitialized... TODO: how to handle this
        else:
            raise NotImplementedError("I'm lazy")

class __extend__(ast.Variable):
    def compile(self, context):
        variable_index = context.variable_indices.get(self.name)
        if variable_index is None:
            raise Exception("Attempt to use undeclared variable %r" % self.name)
        context.emit(bytecode.LOAD_VARIABLE, variable_index)

class __extend__(ast.Call):
    def compile(self, context):
        assert len(self.args) < 256  # technically probably should be smaller?
        for arg in reversed(self.args):
            arg.compile(context)
        context.emit(bytecode.CALL, len(self.args))


def compile(ast):
    context = Context()
    ast.compile(context=context)
    return context.build(name="<don't know>")

def compile_program(program):
    assert isinstance(program, ast.Program)
    for function_ast in program.functions:
        byte_code = compile(function_ast)
        program.compiled_functions[function_ast.name] = byte_code
    return program
