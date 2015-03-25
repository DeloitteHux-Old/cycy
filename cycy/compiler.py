from characteristic import Attribute, attributes

from cycy import bytecode
from cycy.parser import ast


@attributes([
    Attribute(name="instructions", default_factory=list),
    Attribute(name="constants", default_factory=list),
    Attribute(name="variable_indices", default_factory=dict),
])
class Context(object):
    @classmethod
    def to_bytecode(cls, ast, name="<don't know>"):  # TODO: name?
        """
        Build bytecode for the given AST.

        """

        context = cls()
        ast.compile(context=context)
        return context.build(name=name)

    def emit(self, byte_code, arg=-42):
        self.instructions.append(chr(byte_code))
        has_arg, = bytecode.META[byte_code]
        if has_arg:
            assert arg >= 0
            # TODO: could this be more than a byte?
            self.instructions.append(chr(arg))
        else:
            assert arg == -42

    def register_int32_constant(self, int32):
        self.constants.append(int32)
        return len(self.constants) - 1

    def build(self, name):
        return bytecode.Bytecode(
            bytes="".join(self.instructions),
            name=name,
            constants=self.constants,
            number_of_variables=len(self.variable_indices),
        )


class __extend__(ast.BinaryOperation):
    def compile(self, context):
        self.left.compile(context=context)
        self.right.compile(context=context)
        context.emit(bytecode.BINARY_OPERATION_BYTECODE[self.operator])


class __extend__(ast.Int32):
    def compile(self, context):
        index = context.register_int32_constant(self.value)
        context.emit(bytecode.LOAD_CONST, index)
