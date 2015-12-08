from characteristic import Attribute, attributes

from cycy import bytecode
from cycy.exceptions import CyCyError
from cycy.objects import W_Char, W_Function, W_Int32, W_String
from cycy.parser import ast


class NoSuchFunction(CyCyError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return repr(self.name)


@attributes(
    [
        Attribute(name="_instructions", exclude_from_repr=True),
    ],
    apply_with_init=False,
)
class Tape(object):
    """
    A tape carrying the bytecode instructions.

    """

    def __init__(self, instructions=None):
        self._instructions = instructions or []

    def __len__(self):
        return len(self._instructions)

    def __getitem__(self, index):
        return self._instructions[index]

    def __setitem__(self, index, value):
        self._instructions[index] = value

    def emit(self, byte_code, arg=bytecode.NO_ARG):
        self._instructions.append(byte_code)
        self._instructions.append(arg)


@attributes(
    [
        Attribute(name="constants", exclude_from_repr=True),
        Attribute(name="variables", exclude_from_repr=True),
    ],
    apply_with_init=False,
)
class Compiler(object):
    """
    A bytecode compiler.

    .. attribute:: constants

        the :class:`list` of contents that the bytecode indexes into.

        .. note::

            These are C-level objects (i.e. they're wrapped).

    .. attribute:: variables

        a mapping between variable names (:class:`str`\ s) and the
        indices in an array that they should be assigned to

    """

    def __init__(self):
        self.constants = []
        self.variables = {}
        self.functions = {}

    def compile(self, an_ast):
        """
        Compile an AST into bytecode.

        """

        tape = Tape()
        an_ast.compile(tape=tape, compiler=self)
        return bytecode.Bytecode(
            tape=tape,
            name="<don't know>",
            arguments=[],
            constants=self.constants,
            variables=self.variables,
        )

    def register_variable(self, name):
        self.variables[name] = len(self.variables)
        return len(self.variables) - 1

    def register_constant(self, constant):
        self.constants.append(constant)
        return len(self.constants) - 1

    def register_function(self, function):
        self.functions[function.name] = self.register_constant(function)


class __extend__(ast.Program):
    def compile(self, tape, compiler):
        for unit in self.units:
            unit.compile(tape=tape, compiler=compiler)


class __extend__(ast.Function):
    def compile(self, tape, compiler):
        # Register the function AOT, to handle cases where it calls itself.
        function = W_Function(
            name=self.name, arity=len(self.params), bytecode=None,
        )
        compiler.register_function(function)

        function_tape = Tape()
        for param in self.params:
            param.compile(tape=function_tape, compiler=compiler)
        self.body.compile(tape=function_tape, compiler=compiler)

        function.bytecode = bytecode.Bytecode(
            tape=function_tape,
            name="<don't know>",
            arguments=[param.name for param in self.params],
            constants=compiler.constants,
            variables=compiler.variables,
        )


class __extend__(ast.Block):
    def compile(self, tape, compiler):
        for statement in self.statements:
            statement.compile(tape=tape, compiler=compiler)


class __extend__(ast.BinaryOperation):
    def compile(self, tape, compiler):
        # compile RHS then LHS so that their results end up on the stack
        # in reverse order; then we can pop in order in the interpreter
        self.right.compile(tape=tape, compiler=compiler)
        self.left.compile(tape=tape, compiler=compiler)
        tape.emit(bytecode.BINARY_OPERATION_BYTECODE[self.operator])


class __extend__(ast.Int32):
    def compile(self, tape, compiler):
        wrapped = W_Int32(value=self.value)
        index = compiler.register_constant(wrapped)
        tape.emit(bytecode.LOAD_CONST, index)


class __extend__(ast.Char):
    def compile(self, tape, compiler):
        wrapped = W_Char(char=self.value)
        index = compiler.register_constant(wrapped)
        tape.emit(bytecode.LOAD_CONST, index)


class __extend__(ast.Assignment):
    def compile(self, tape, compiler):
        self.right.compile(tape=tape, compiler=compiler)
        index = compiler.variables.get(self.left.name, -42)
        if index == -42:
            raise Exception("Attempt to use undeclared variable '%s'" % self.left.name)
        tape.emit(bytecode.STORE_VARIABLE, index)


class __extend__(ast.String):
    def compile(self, tape, compiler):
        wrapped = W_String(value=self.value)
        index = compiler.register_constant(wrapped)
        tape.emit(bytecode.LOAD_CONST, index)


class __extend__(ast.ReturnStatement):
    def compile(self, tape, compiler):
        if self.value:
            self.value.compile(tape=tape, compiler=compiler)
        tape.emit(bytecode.RETURN, int(bool(self.value)))


class __extend__(ast.For):
    def compile(self, tape, compiler):
        jump_ix = len(tape)
        self.condition.compile(tape=tape, compiler=compiler)
        jump_nz = len(tape)
        tape.emit(bytecode.JUMP_IF_ZERO, 0)
        self.body.compile(tape=tape, compiler=compiler)
        tape.emit(bytecode.JUMP, jump_ix)
        tape[jump_nz + 1] = len(tape)


class __extend__(ast.VariableDeclaration):
    def compile(self, tape, compiler):
        vtype = self.vtype
        assert isinstance(vtype, ast.Type)

        if vtype.base_type == "int" and vtype.length == 32:
            variable_index = compiler.register_variable(self.name)
            if self.value:
                self.value.compile(tape=tape, compiler=compiler)
                tape.emit(bytecode.STORE_VARIABLE, variable_index)
            # else we've declared the variable, but it is
            # uninitialized... TODO: how to handle this
        elif vtype.base_type == "pointer":
            ref = vtype.reference
            assert isinstance(ref, ast.Type)
            if ref.base_type == "int" and ref.length == 8:
                variable_index = compiler.register_variable(self.name)
                if self.value:
                    self.value.compile(tape=tape, compiler=compiler)
                    tape.emit(bytecode.STORE_VARIABLE, variable_index)
        else:
            raise NotImplementedError("Variable type %s not supported" % vtype)


class __extend__(ast.Variable):
    def compile(self, tape, compiler):
        variable_index = compiler.variables.get(self.name, -42)
        if variable_index == -42:
            # XXX: this should be either a runtime or compile time exception
            raise Exception("Attempt to use undeclared variable '%s'" % self.name)
        tape.emit(bytecode.LOAD_VARIABLE, variable_index)


class __extend__(ast.Call):
    def compile(self, tape, compiler):
        arity = len(self.args)
        assert arity < 256  # technically probably should be smaller?
        for arg in reversed(self.args):
            arg.compile(tape=tape, compiler=compiler)
        if self.name == "putchar":
            # TODO we should implement putchar in bytecode once we have
            # working asm blocks
            tape.emit(bytecode.PUTC, bytecode.NO_ARG)
            return
        index = compiler.functions.get(self.name)
        if index is None:
            raise NoSuchFunction(self.name)
        tape.emit(bytecode.CALL, index)


class __extend__(ast.ArrayDereference):
    def compile(self, tape, compiler):
        self.index.compile(tape=tape, compiler=compiler)
        self.array.compile(tape=tape, compiler=compiler)

        tape.emit(bytecode.DEREFERENCE, bytecode.NO_ARG)
