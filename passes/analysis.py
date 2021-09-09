"""Micro-C Program Analysis Pass"""

from itertools import product

from lang.ops import *

from utils.decorators import classproperty


class UCReachingDefs:
    """Reaching definitions analysis"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.rd = {}

    @classproperty
    def jolly_node(cls):
        return '?'

    @property
    def nodes_ex(self):
        return list(self.cfg.nodes) + [UCReachingDefs.jolly_node]

    def killset(self, u, v):
        uv = self.cfg.edges[u, v]
        a = uv['action']

        if isinstance(a, UCAssignment):
            if isinstance(a.lhs, UCArrayDeref):
                var_id = a.lhs.oprs[0]
            elif isinstance(a.lhs, UCRecordDeref):
                var_id = a.lhs.oprs[0]
            else:
                var_id = a.lhs

            var = self.cfg.vars[var_id]

            if isinstance(var, UCArray):
                return []
            elif isinstance(var, UCRecord):
                return []
            else:
                return product([var_id], self.nodes_ex, self.cfg.nodes)
        else:
            return []

    def genset(self, u, v):
        uv = self.cfg.edges[u, v]
        a = uv['action']

        if isinstance(a, UCAssignment):
            if isinstance(a.lhs, UCArrayDeref):
                var_id = a.lhs.oprs[0]
            elif isinstance(a.lhs, UCRecordDeref):
                var_id = a.lhs.oprs[0]
            else:
                var_id = a.lhs

            var = self.cfg.vars[var_id]

            if isinstance(var, UCVariable):
                return [(var_id, u, v,)]
        else:
            return []

    def compute(self, copy=False):
        kill = {}
        gen = {}
        rd = {}

        # Compute kill- and gensets
        for u, v in self.cfg.edges:
            kill[(u, v,)] = set(self.killset(u, v))
            gen[(u, v,)] = set(self.genset(u, v))

        # Compute initial RD assignments
        for q in self.cfg.nodes:
            if q not in self.cfg.sources:
                rd[q] = set()

        rd[self.cfg.sources[0]] = set(product(self.cfg.vars,
                                              [UCReachingDefs.jolly_node],
                                              [self.cfg.sources[0]]))

        # Compute the MOP solution for RD assignments
        refine = True

        while refine:
            refine = False

            for u, v in self.cfg.edges:
                kill_uv = kill[(u, v,)]
                gen_uv = gen[(u, v,)]

                rd_u_not_kill_uv = rd[u].difference(kill_uv)

                if not rd_u_not_kill_uv.union(gen_uv).issubset(rd[v]):
                    rd[v] = rd[v].union(rd_u_not_kill_uv).union(gen_uv)
                    refine = True

        if copy:
            return rd

        self.rd = rd

    def __str__(self):
        s = ''

        for q, rds in self.rd.items():
            s += f'RD({q}): '

            for rd in rds:
                s += f'({str(rd[0])}, {rd[1]}, {rd[2]})' + ', '
            s = s.removesuffix(', ') + '\n'

        return s
