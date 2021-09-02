""""Micro-C Arithmetic and Logical Operations"""
from ucast import *
from uctypes import *

class UCUnOp(UCASTNode):
    """Micro-C Unary Op"""
    def __init__(self, op, opr):
        super().__init__(op, [opr])
        self.op = op
        self.opr = opr
    
    def __str__(self):
        return f'({self.op} {self.opr})'

class UCNot(UCUnOp):
    """Micro-C Not Op"""
    def __init__(self, opr):
        super().__init__('!', opr)

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

class UCExprBinOp(UCExpression):
    """Micro-C Expression Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, [lhs, rhs])
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

class UCABinOp(UCExprBinOp):
    """Micro-C Arithmetic Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

class UCBBinOp(UCExprBinOp):
    """Micro-C Boolean Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)

class UCRBinOp(UCExprBinOp):
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

class UCEqq(UCBinOp):
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