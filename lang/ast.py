"""Abstract Syntax Tree for Micro-C"""
import inspect

from functools import reduce


class UCASTNode:
    """Micro-C AST Node"""

    def __init__(self, key, children=None, lineno=None):
        self.key = key
        self.lineno = lineno
        self.children = []

        if children is not None:
            for child in children:
                    self.add_child(child)

    def add_child(self, node):
        if node is not None:
            self.children.append(node)

    def __eq__(self, other):
        if isinstance(other, UCASTNode):
            return self.key == other.key and \
                self.lineno == other.lineno and \
                len(self.children) == len(other.children) and \
                reduce(lambda b1, b2: b1 and b2,
                       [x == y for x, y in zip(self.children, other.children)],
                       True)

        return False

    def __str__(self):
        def str_aux(root, depth=0):
            if root == None:
                return ''

            node_types = ''

            for node_ty in inspect.getmro(type(root))[:-2]:
                node_types += node_ty.__name__ + ' -> '
            node_types = '(' + node_types.removesuffix(' -> ') + ')'

            if root.lineno != None:
                node_types += f' - line {root.lineno}'

            key = f'{root.key} ' if root.key != None else ''

            s = '\t' * depth + f'{key}{node_types}\n'

            for child in root.children:
                s += str_aux(child, depth + 1)
            return s

        return str_aux(self)
