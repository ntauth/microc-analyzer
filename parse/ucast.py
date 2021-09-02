"""Abstract Syntax Tree for Micro-C"""
import inspect

class UCASTNode:
    """Tree node"""
    def __init__(self, key, children=None):
        self.key = key

        if children == None:
            self.children = []
        else:
            self.children = children

    def add_child(self, node):
        if node != None:
            self.children.append(node)

class UCASTUtils:
    @staticmethod
    def dfs_visit(root, verbose=True, depth=0):
        if root == None:
            return

        node_types = ''

        if verbose:
            for node_ty in inspect.getmro(type(root))[:-2]:
                node_types += node_ty.__name__ + ' -> '
            node_types = '(' + node_types.removesuffix(' -> ') + ')'

        key = f'{root.key} ' if root.key != None else ''

        print('\t' * depth + f'{key}{node_types}')

        for child in root.children:
            UCASTUtils.dfs_visit(child, verbose, depth + 1)
