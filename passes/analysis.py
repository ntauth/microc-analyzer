"""Micro-C Program Analysis Pass"""

from itertools import product

from lang.ops import *

from utils.decorators import classproperty


class UCReachingDefs:
    """Reaching definitions analysis"""

    def __init__(self, cfg):
        self.cfg = cfg

    @classproperty
    def jolly_node(cls):
        return '?'

    @property
    def nodes_ex(self):
        return list(self.cfg.nodes) + [UCReachingDefs.jolly_node]

    def killset(self, u, v):
        e = self.cfg.edges[u, v]
        a = e['action']

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
                return list(product([var_id], self.nodes_ex, self.cfg.nodes))
        else:
            return []

    def genset(self, u, v):
        e = self.cfg.edges[u, v]
        a = e['action']

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

    def compute(self):
        kill = {}
        gen = {}
        rd = {}

        # Compute kill- and gensets
        for u, v in self.cfg.edges:
            kill[(u, v,)] = self.killset(u, v)
            gen[(u, v,)] = self.genset(u, v)

        # Compute initial RD assignments
        for q in self.cfg.nodes:
            if q not in self.cfg.sources_keys:
                rd[q] = []

        rd[self.cfg.sources_keys[0]] = set(product(self.cfg.vars,
                                                    [UCReachingDefs.jolly_node],
                                                    [self.cfg.sources_keys[0]]))

        # for e, ks in kill.items():
        #     print(f'{e}: {list(map(lambda e: (str(e[0]), e[1], e[2],), list(ks)))}')
        # print()
        # for e, gs in gen.items():
        #     print(f'{e}: {list(map(lambda e: (str(e[0]), e[1], e[2],), list(gs)))}')
        # print()  
        # for q, rds in rd.items():
        #     print(f'{q}: {list(map(lambda e: (str(e[0]), e[1], e[2],), list(rds)))}')
        # print()

        # Compute the MOP solution for RD assignments
        refine = True

        while refine:
            refine = False

            for u, v in self.cfg.edges:
                rd_u = set(rd[u])
                rd_v = set(rd[v])
                kill_uv = set(kill[(u, v,)])
                gen_uv = set(gen[(u, v,)])
 
                if not rd_u.difference(kill_uv).union(gen_uv).issubset(rd_v):
                    rd[v] = rd_v.union(rd_u.difference(kill_uv)).union(gen_uv)
                    refine = True

        return rd
