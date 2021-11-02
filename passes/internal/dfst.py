"""Spanning Tree Algorithms"""

import networkx as nx


class UCSpanTree:
    @staticmethod
    def sort_rp(rp):
        return dict(sorted(rp.items(), key=lambda x: x[1]))

    @staticmethod
    def dfs_tree(cfg, source=None):
        tree_nodes, tree_edges = set(), set()
        rp = dict()
        k = len(cfg.nodes)

        def dfs_visit(x):
            nonlocal tree_nodes, tree_edges, rp, k

            tree_nodes.add(x)

            for y in cfg.successors(x):
                if y not in tree_nodes:
                    tree_edges.add((x, y,))
                    dfs_visit(y)
            
            rp[x] = k
            k -= 1
        
        if source is None:
            source = cfg.source
        
        dfs_visit(source)

        return rp, nx.DiGraph(tree_edges)
