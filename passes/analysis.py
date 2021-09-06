"""Micro-C Program Analysis Pass"""

from itertools import product

from lang.ops import *


class UCReachingDefs:
    """Reaching definitions analysis"""
    def __init__(self, cfg):
        self.cfg = cfg
    
    @property
    def nodes_ex(self):
        return list(self.cfg.nodes) + ['?']

    def killset(self, u, v):
        e = self.cfg.edges[u, v]
        a = e['action']

        if isinstance(a, UCAssignment):
            return list(product([a], self.nodes_ex, self.cfg.nodes))