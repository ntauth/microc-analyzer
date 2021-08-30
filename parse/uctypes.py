"""Micro-C Type Definitions"""

class UCVariable:
    """Micro-C Variable"""
    def __init__(self, type, id, value=0):
        self._type  = type
        self._id = id
        self._value = value

    def __str__(self):
        return f'{self._type} {self._id} = {self._value}'

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
    """Micro-C Variable"""
    def __init__(self, type, id, vars={}):
        super().__init__(type, id, vars)

    def __str__(self):
        value = '{' + ', '.join([str(v) for _, v in self._value.items()]) + '}'

        return f'{self._type} {self._id} = {value}'

class UCArray(UCVariable):
    """Micro-C Array"""
    def __init__(self, type, id, size, values=[0]):
        super().__init__(type, id, values)
        self.size = size
        
        if len(values) == size:
            self.value = [UCVariable(type, f'{id}[{i}]', values[i]) for i in range(len(values))]
        elif len(values) < size:
            self.value = [UCVariable(type, f'{id}[{i}]', values[i]) for i in range(len(values))] + \
                         [UCVariable(type, f'{id}[{i}]', 0) for i in range(self.size - len(values), self.size + 1)]
        else:
            raise ValueError('Initializer list is bigger than the holding array')
    
    def __str__(self):
        value = '[' + ', '.join([str(v.value) for v in self._value]) + ']'
        return f'{self.type}[{self.size}] {self.id} = {value}'
