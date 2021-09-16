"""Micro-C Program Analysis Pass"""

from itertools import product

from lang.ops import *
from utils.decorators import classproperty

from .internal.worklist import *


class UCReachingDefs:
    """Reaching definitions analysis"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.rd = {}
        self.iters = -1

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
            if q != self.cfg.source:
                rd[q] = set()

        rd[self.cfg.source] = set(product(self.cfg.vars,
                                              [UCReachingDefs.jolly_node],
                                              [self.cfg.source]))

        # Compute the MOP solution for RD assignments
        ucw = UCWorklist(self.cfg, kill, gen, rd, strategy=UCRRStrategy)
        self.iters = ucw.compute()

        if copy:
            return rd

        self.rd = rd

    def __str__(self):
        s = f'{type(self).__name__} analysis performed in {self.iters} iterations.\n\n'

        for q, rds in self.rd.items():
            s += f'RD({q}): '

            for rd in rds:
                s += f'({str(rd[0])}, {rd[1]}, {rd[2]})' + ', '
            s = s.removesuffix(', ') + '\n'

        return s


class UCLiveVars:
    """Live variable analysis"""

    def __init__(self, cfg):
        self.cfg = cfg.reverse()
        self.lv = {}
        self.iters = -1

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
                return [var_id]
        else:
            return []

    def __genset(self, node, storage):
        if isinstance(node, UCRecordInitializerList):
            self.__genset(node.values[0], storage)
            self.__genset(node.values[1], storage)
        elif isinstance(node, UCArrayDeref):
            storage.append(node.lhs)
            self.__genset(node.rhs, storage)
        elif isinstance(node, UCNot):
            self.__genset(node.opr.lhs, storage)
            self.__genset(node.opr.rhs, storage)
        elif isinstance(node, UCIdentifier):
            storage.append(node)
            return
        elif isinstance(node, UCNumberLiteral):
            return
        elif isinstance(node, UCBoolLiteral):
            return
        else:
            self.__genset(node.lhs, storage)
            self.__genset(node.rhs, storage)

    def genset(self, u, v):
        uv = self.cfg.edges[u, v]
        a = uv['action']

        storage = []
        if isinstance(a, UCAssignment):
            if isinstance(a.lhs, UCArrayDeref):
                self.__genset(a.lhs.oprs[1], storage)
            self.__genset(a.rhs, storage)
        elif isinstance(a, UCExprBinOp):
            self.__genset(a.lhs, storage)
            self.__genset(a.rhs, storage)
        elif isinstance(a, UCCall):
            self.__genset(a.args[0], storage)
        elif isinstance(a, UCNot):
            self.__genset(a.opr.lhs, storage)
            self.__genset(a.opr.rhs, storage)

        return list(set(storage))

    def compute(self, copy=False):
        kill = {}
        gen = {}
        lv = {}

        # Compute kill- and gensets
        for u, v in self.cfg.edges:
            kill[(u, v,)] = set(self.killset(u, v))
            gen[(u, v,)] = set(self.genset(u, v))

        # # Compute initial LV assignments
        for q in self.cfg.nodes:
            lv[q] = set()

        # Compute the MOP solution for LV assignments
        ucw = UCWorklist(self.cfg, kill, gen, lv, strategy=UCRRStrategy)
        self.iters = ucw.compute()

        if copy:
            return lv

        self.lv = lv

    def __str__(self):
        s = f'{type(self).__name__} analysis performed in {self.iters} iterations.\n\n'

        for q, lvs in self.lv.items():
            s += f'LV({q}): '

            lvs_a = []
            for lv in lvs:
                lvs_a.append(str(lv))
            for lv in sorted(lvs_a):
                s += lv + ', '
            s = s.removesuffix(', ') + '\n'

        return s
