"""Micro-C Type Definitions"""
from ucast import *

class UCBlock(UCASTNode):
    """Micro-C Code Block"""
    def __init__(self, decls, stmts):
        super().__init__('__uc_block__', [decls, stmts])
        self.decls = decls
        self.stmts = stmts

class UCDeclarations(UCASTNode):
    """Micro-C Declaration Sub-block"""
    def __init__(self, decls=None):
        super().__init__('__uc_decls__', decls)
        self.decls = decls

class UCStatements(UCASTNode):
    """Micro-C Statement Sub-block"""
    def __init__(self, stmts=None):
        super().__init__('__uc_stmts__', stmts)
        self.stmts = stmts

class UCVariable(UCASTNode):
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

class UCIdentifier(UCASTNode):
    """Micro-C Identifier"""
    def __init__(self, id):
        super().__init__(id)
        self.id = id

    def __str__(self):
        return self.id

class UCNumberLiteral(UCASTNode):
    """Micro-C Number Literal"""
    def __init__(self, value):
        super().__init__(str(value))
        self._value = value
    
    @property
    def value(self):
        return int(self._value)