""""Micro-C Arithmetic and Logical Operations"""
from ucast import *

class UCUnOp(UCASTNode):
    """Micro-C Unary Op"""
    def __init__(self, op, opr):
        super().__init__(op, [opr])
        self.op = op
        self. opr = opr
    
    def __str__(self):
        return f'({self.op} {self.opr})'

class UCNot(UCUnOp):
    """Micro-C Not Op"""
    def __init__(self, opr):
        super().__init__('!', [opr])

# TODO: Make abstract and nest concrete op classes inside it
class UCBinOp(UCASTNode):
    """Micro-C Binary Op"""
    def __init__(self, op, lhs, rhs):
        super().__init__(op, [lhs, rhs])
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self):
        return f'({self.op} {self.lhs} {self.rhs})'

class UCAdd(UCBinOp):
    """Micro-C `+` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('+', lhs, rhs)

class UCSub(UCBinOp):
    """Micro-C `-` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('-', lhs, rhs)

class UCMod(UCBinOp):
    """Micro-C `%` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('%', lhs, rhs)

class UCDiv(UCBinOp):
    """Micro-C `/` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('/', lhs, rhs)

class UCMul(UCBinOp):
    """Micro-C `*` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('*', lhs, rhs)

class UCAnd(UCBinOp):
    """Micro-C `&` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('&', lhs, rhs)

class UCOr(UCBinOp):
    """Micro-C `|` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('|', lhs, rhs)

class UCLt(UCBinOp):
    """Micro-C `<` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('<', lhs, rhs)

class UCLte(UCBinOp):
    """Micro-C `<=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('<=', lhs, rhs)

class UCGt(UCBinOp):
    """Micro-C `>` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('>', lhs, rhs)

class UCGte(UCBinOp):
    """Micro-C `>=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('>=', lhs, rhs)

class UCEq(UCBinOp):
    """Micro-C `==` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('==', lhs, rhs)

class UCNeq(UCBinOp):
    """Micro-C `!=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('!=', lhs, rhs)

class UCEqq(UCBinOp):
    """Micro-C `:=` operator"""
    def __init__(self, lhs, rhs):
        super().__init__(':=', lhs, rhs)

class UCArrayDeref(UCBinOp):
    """Micro-C `[]` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('[]', lhs, rhs)

class UCRecordDeref(UCBinOp):
    """Micro-C `.` operator"""
    def __init__(self, lhs, rhs):
        super().__init__('.', lhs, rhs)