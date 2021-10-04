"""Micro-C Program Analysis Pass"""

import math

from itertools import product

from networkx.algorithms.operators.all import union_all

from lang.ops import *
from utils.decorators import classproperty

from .internal.worklist import *


class UCAnalysis:
    """Micro-C Program Analysis"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.asgn = {}
        self.iters = -1

    @classproperty
    def jolly_node(cls):
        return '?'

    @property
    def nodes_ex(self):
        return list(self.cfg.nodes) + [UCReachingDefs.jolly_node]

    def fv(self, u, v):
        uv = self.cfg.edges[u, v]
        a = uv['action']

        def fv_aux(a):
            fv = set()

            if isinstance(a, UCIdentifier):
                fv.add(a)
            elif isinstance(a, UCArrayDeref):
                fv.add(a.lhs)
                fv = fv.union(fv_aux(a.rhs))
            elif isinstance(a, UCRecordDeref):
                fv.add(a.lhs)
            else:
                for a_ in a.children:
                    fv = fv.union(fv_aux(a_))

            return fv

        if isinstance(a, UCAssignment):
            if isinstance(a.lhs, UCArrayDeref):
                return set.union(fv_aux(a.lhs.rhs), fv_aux(a.rhs))
            else:
                return fv_aux(a.rhs)
        elif isinstance(a, UCBExpression):
            return fv_aux(a)
        else:
            return set()

    @abstractmethod
    def __str__(self, pfx, fmt, forward=True):
        s = f'{type(self).__name__} analysis performed in {self.iters} iterations.\n\n'

        source_key = -1 if forward else math.inf
        sink_key = math.inf if forward else -1

        def sort_pred(kv): return int(kv[0])\
            if kv[0] not in [self.cfg.source, self.cfg.sink]\
            else (source_key if kv[0] == self.cfg.source else sink_key)

        for q, asgns in sorted(self.asgn.items(), key=sort_pred):
            s += f'{pfx}({q}): '

            if len(asgns) > 0:
                for asgn in asgns:
                    s += fmt(asgn) + ', '
            else:
                s += '∅'

            s = s.removesuffix(', ') + '\n'

        return s


class UCReachingDefs(UCAnalysis):
    """Reaching definitions analysis"""

    def __init__(self, cfg):
        super().__init__(cfg)

    @property
    def update_fn(self):
        def update_fn_impl(R, u, v):
            kill_uv = set(self.killset(u, v))
            gen_uv = set(self.genset(u, v))

            rd_u_not_kill_uv = R[u].difference(kill_uv)

            if not rd_u_not_kill_uv.union(gen_uv).issubset(R[v]):
                R[v] = R[v].union(
                    rd_u_not_kill_uv).union(gen_uv)
                return True

            return False

        return update_fn_impl

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

        # Compute the MFP solution for RD assignments
        ucw = UCWorklist(self.cfg, self.update_fn, rd, strategy=UCLIFOStrategy)
        self.iters = ucw.compute()

        if copy:
            return rd

        self.asgn = rd

    def __str__(self):
        return super().__str__(
            'RD', lambda asgn: f'({str(asgn[0])}, {asgn[1]}, {asgn[2]})')


class UCLiveVars(UCAnalysis):
    """Live variable analysis"""

    def __init__(self, cfg):
        super().__init__(cfg.reverse())

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

    @property
    def update_fn(self):
        def update_fn_impl(R, u, v):
            kill_uv = set(self.killset(u, v))
            gen_uv = set(self.genset(u, v))

            rd_u_not_kill_uv = R[u].difference(kill_uv)

            if not rd_u_not_kill_uv.union(gen_uv).issubset(R[v]):
                R[v] = R[v].union(
                    rd_u_not_kill_uv).union(gen_uv)
                return True

            return False

        return update_fn_impl

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

        # Compute initial LV assignments
        for q in self.cfg.nodes:
            lv[q] = set()

        # Compute the MOP solution for LV assignments
        ucw = UCWorklist(self.cfg, self.update_fn, lv, strategy=UCRRStrategy)
        self.iters = ucw.compute()

        # Sort LV assignment vales by identifier
        lv = {k: sorted(v, key=lambda v: str(v)) for k, v in lv.items()}

        if copy:
            return lv

        self.asgn = lv

    def __str__(self):
        return super().__str__('LV', lambda asgn: f'{str(asgn)}', forward=False)


class UCDangerousVars(UCAnalysis):
    """UC Dangerous Vars"""

    def __init__(self, cfg):
        super().__init__(cfg)

    @property
    def update_fn(self):
        def update_fn_impl(R, u, v):
            uv = self.cfg.edges[u, v]
            a = uv['action']
            fv = set(self.fv(u, v))

            updated = False

            if isinstance(a, UCAssignment):
                # x := a
                if isinstance(a.lhs, UCIdentifier):
                    if fv.intersection(R[u]) == set():
                        if not R[u].difference([a.lhs]).issubset(R[v]):
                            R[v] = R[v].union(R[u].difference([a.lhs]))
                            updated = True
                    else:
                        if not R[u].union([a.lhs]).issubset(R[v]):
                            R[v] = R[v].union(R[u].union([a.lhs]))
                            updated = True
                # A[a1] := a2
                elif isinstance(a.lhs, UCArrayDeref):
                    if fv.intersection(R[v]) != set():
                        if not R[u].union([a.lhs.lhs]).issubset(R[v]):
                            R[v] = R[v].union(R[u].union([a.lhs.lhs]))
                            updated = True
                # R.fst := a
                elif isinstance(a.lhs, UCRecordDeref):
                    if fv.intersection(R[v]) != set():
                        if not R[u].union([a.lhs.lhs]).issubset(R[v]):
                            R[v] = R[v].union(R[u].union([a.lhs.lhs]))
                            updated = True
            else:
                if not R[u].issubset(R[v]):
                    R[v] = R[u]
                    updated = True

            return updated

        return update_fn_impl

    def compute(self, copy=False):
        dv = {}

        # DV=RD for the initial assignment
        rd = UCReachingDefs(self.cfg)
        rd.compute()

        # Lift the assignment to the correct analysis domain
        # and only add initial definitions
        for q, rds in rd.asgn.items():
            dv[q] = set()

            for rd_ in rds:
                # Is it an initial definition?
                if rd_[1] == self.jolly_node:
                    dv[q].add(rd_[0])

        # Debug free variables
        # TODO: Remove once sure that fv works as expected
        # for u, v in self.cfg.edges:
        #     print(f'{u}, {v}: {list(map(lambda v: str(v.id), self.fv(u, v)))}')

        # Compute the MOP solution for DV assignments
        ucw = UCWorklist(self.cfg, self.update_fn, dv, strategy=UCLIFOStrategy)
        self.iters = rd.iters + ucw.compute()

        if copy:
            return dv

        self.asgn = dv

    def __str__(self):
        return super().__str__('DV', lambda dv: f'{str(dv)}')
