"""Spanning Tree Algorithms"""

class UCSpanTree:
    @staticmethod
    def dfs_tree(cfg, source=None):
        def dfs_visit(x):
            ...
        
        if source is None:
            source = cfg.source
        
        dfs_visit(source)