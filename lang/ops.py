""""Micro-C Arithmetic and Logical Operations"""
from .ast import *
from .types import *

class UCUnOp(UCASTNode):
    """Micro-C Unary Op"""
    def __init__(self, op, opr):
        super().__init__(op, [opr])
        self.op = op
        self.opr = opr
    
    def __str__(self):
        return f'({self.op} {self.opr})'

class UCExprUnOp(UCBExpression):
    """Micro-C Expression Unary Op"""
    def __init__(self, op, opr):
        super().__init__(op, [opr])
        self.op = op
        self.opr = opr
    
    def __str__(self):
        return f'({self.op} {self.opr})'

class UCNot(UCExprUnOp):
    """Micro-C Not Op"""
    def __init__(self, opr):
        super().__init__('!', opr)
        self.opr = opr

# TODO: Make abstract and nest concrete op classes inside it
class UCBinOp(UCStatement):
    """Micro-C Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, [lhs, rhs])
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

class UCAExprBinOp(UCAExpression):
    """Micro-C Arithmetic Expression Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, [lhs, rhs])
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

class UCBExprBinOp(UCBExpression):
    """Micro-C Boolean Expression Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, [lhs, rhs])
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

class UCRExprBinOp(UCRExpression):
    """Micro-C Relational Expression Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, [lhs, rhs])
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

class UCABinOp(UCAExprBinOp):
    """Micro-C Arithmetic Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

class UCBBinOp(UCBExprBinOp):
    """Micro-C Boolean Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

class UCRBinOp(UCRExprBinOp):
    """Micro-C Relational Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

class UCAdd(UCABinOp):
    """Micro-C `+` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('+', lhs, rhs)

class UCSub(UCABinOp):
    """Micro-C `-` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('-', lhs, rhs)

class UCMod(UCABinOp):
    """Micro-C `%` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('%', lhs, rhs)

class UCDiv(UCABinOp):
    """Micro-C `/` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('/', lhs, rhs)

class UCMul(UCABinOp):
    """Micro-C `*` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('*', lhs, rhs)

class UCAnd(UCBBinOp):
    """Micro-C `&` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('&', lhs, rhs)

class UCOr(UCBBinOp):
    """Micro-C `|` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('|', lhs, rhs)

class UCLt(UCRBinOp):
    """Micro-C `<` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('<', lhs, rhs)

class UCLte(UCRBinOp):
    """Micro-C `<=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('<=', lhs, rhs)

class UCGt(UCRBinOp):
    """Micro-C `>` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('>', lhs, rhs)

class UCGte(UCRBinOp):
    """Micro-C `>=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('>=', lhs, rhs)

class UCEq(UCRBinOp):
    """Micro-C `==` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('==', lhs, rhs)

class UCNeq(UCRBinOp):
    """Micro-C `!=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('!=', lhs, rhs)

class UCAssignment(UCBinOp):
    """Micro-C `:=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__(':=', lhs, rhs)

class UCArrayDeref(UCABinOp):
    """Micro-C `[]` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('[]', lhs, rhs)

class UCRecordDeref(UCABinOp):
    """Micro-C `.` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('.', lhs, rhs)