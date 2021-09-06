"""Micro-C Type Definitions"""
from .ucast import *


class UCProgram(UCASTNode):
    """Micro-C Source Unit"""

    def __init__(self, blocks=None):
        super().__init__(None, blocks)
        self.blocks = blocks


class UCBlock(UCASTNode):
    """Micro-C Code Block"""

    def __init__(self, decls=None, stmts=None):
        super().__init__(None, [decls, stmts])
        self.decls = decls
        self.stmts = stmts


class UCNestedBlock(UCBlock):
    """Micro-C Nested Block (statements only)"""

    def __init__(self, stmts=None):
        super().__init__(None, stmts)


class UCDeclarations(UCASTNode):
    """Micro-C Declaration Sub-block"""

    def __init__(self, decls=None):
        super().__init__(None, decls)
        self.decls = decls


class UCDeclaration(UCASTNode):
    """Micro-C Declaration"""

    def __init__(self, ty, oprs=None):
        super().__init__(ty, oprs)
        self.ty = ty
        self.oprs = oprs


class UCStatements(UCASTNode):
    """Micro-C Statement Sub-block"""

    def __init__(self, stmts=None):
        super().__init__(None, stmts)
        self.stmts = stmts


class UCStatement(UCASTNode):
    """Micro-C Statement"""

    def __init__(self, ty, oprs=None):
        super().__init__(ty, oprs)
        self.ty = ty
        self.oprs = oprs

# TODO: Subclass UCStatement


class UCIf(UCStatement):
    """Micro-C If Statement"""

    def __init__(self, b_expr, block):
        super().__init__(None, [b_expr, block])
        self.b_expr = b_expr
        self.block = block

# TODO: Subclass UCStatement


class UCIfElse(UCStatement):
    """Micro-C If-Else Statement"""

    def __init__(self, b_expr, if_block, else_block):
        super().__init__(None, [b_expr, if_block, else_block])
        self.b_expr = b_expr
        self.if_block = if_block
        self.else_block = else_block

# TODO: Subclass UCStatement


class UCWhile(UCStatement):
    """Micro-C While Statement"""

    def __init__(self, b_expr, block):
        super().__init__(None, [b_expr, block])
        self.b_expr = b_expr
        self.block = block

# TODO: Subclass UCStatement


class UCCall(UCStatement):
    """Micro-C Call Statement"""

    def __init__(self, fn, args):
        super().__init__(None, [fn] + args)
        self.fn = fn
        self.args = args


class UCExpression(UCASTNode):
    """Micro-C Expression"""

    def __init__(self, op, oprs=None):
        super().__init__(op, oprs)
        self.op = op
        self.oprs = oprs


class UCLExpression(UCExpression):
    """Micro-C LValue Expression"""

    def __init__(self, op, oprs=None):
        super().__init__(op, oprs)


class UCAExpression(UCExpression):
    """Micro-C Arithmetic Expression"""

    def __init__(self, op, oprs=None):
        super().__init__(op, oprs)


class UCBExpression(UCExpression):
    """Micro-C Boolean Expression"""

    def __init__(self, op, oprs=None):
        super().__init__(op, oprs)


class UCRecordInitializerList(UCASTNode):
    """Micro-C Record Initializer List"""

    def __init__(self, values):
        super().__init__(None, values)
        self.values = values

    def __str__(self):
        s = ', '.join(list(map(str, self.values)))
        return f'({s})'


class UCVariable(UCDeclaration):
    """Micro-C Variable"""

    def __init__(self, type, id, value=0):
        super().__init__(f'{id}')
        self._type = type
        self._id = id
        self._value = value

    def __str__(self):
        return f'{self._id}'

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class UCField(UCASTNode):
    """Micro-C Field"""

    def __init__(self, type, id, value=0):
        super().__init__(f'{id}')
        self._type = type
        self._id = id
        self._value = value

    def __str__(self):
        return f'{self._id}'

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class UCRecord(UCVariable):
    """Micro-C Record"""

    def __init__(self, type, id, fields=None):
        super().__init__(type, id, fields)

        if fields == None:
            self.fields = fields

    def __str__(self):
        return f'{self._id}'


class UCArray(UCVariable):
    """Micro-C Array"""

    def __init__(self, type, id, size, values=None):
        super().__init__(type, id, values)
        self.size = size

        # TODO: Obsolete
        # if values == None:
        #     values = [0]

        # if len(values) == size.value:
        #     self.value = [UCVariable(type, f'{id}[{i}]', values[i]) for i in range(len(values))]
        # elif len(values) < size.value:
        #     self.value = [UCVariable(type, f'{id}[{i}]', values[i]) for i in range(len(values))] + \
        #                  [UCVariable(type, f'{id}[{i}]', 0) for i in range(self.size - len(values), self.size + 1)]
        # else:
        #     raise ValueError('Initializer list is bigger than the holding array')

    def __str__(self):
        return f'{self.type}[{self.size}] {self.id}'


class UCIdentifier(UCAExpression):
    """Micro-C Identifier"""

    def __init__(self, id):
        super().__init__(id)
        self.id = id

    def __str__(self):
        return self.id


class UCBuiltinIdentifier(UCASTNode):
    """Micro-C Built-in Identifier"""

    def __init__(self, id):
        super().__init__(id)
        self.id = id

    def __str__(self):
        return self.id


class UCNumberLiteral(UCLExpression):
    """Micro-C Number Literal"""

    def __init__(self, value):
        super().__init__(str(value))
        self._value = value

    @property
    def value(self):
        return int(self._value)

    def __str__(self):
        return str(self.value)


class UCBoolLiteral(UCBExpression):
    """Micro-C Bool Literal"""

    def __init__(self, value):
        super().__init__(bool(value))
        self._value = value

    @property
    def value(self):
        return bool(self._value)

    def __str__(self):
        return self.value
