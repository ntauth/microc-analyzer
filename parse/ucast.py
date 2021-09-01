"""Abstract Syntax Tree for Micro-C"""

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
    def dfs_visit(root, depth=0):
        if root == None:
            return

        print('\t' * depth + f'({type(root).__name__}) {root.key}')

        for child in root.children:
            UCASTUtils.dfs_visit(child, depth + 1)
