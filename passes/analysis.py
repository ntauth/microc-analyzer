"""Micro-C Program Analysis Pass"""

import math

from itertools import product
from functools import reduce

from lang.ops import *
from utils.decorators import classproperty

from .internal.worklist import *


class UCAnalysis:
    """Micro-C Program Analysis"""

    def __init__(self, cfg):
        self.cfg = cfg
        self.aa = {}
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

        for q, aa_ in sorted(self.aa.items(), key=sort_pred):
            s += f'{pfx}({q}): '

            if len(aa_) > 0:
                for ae in aa_.items() if isinstance(aa_, dict) else aa_:
                    s += fmt(ae) + ', '
            else:
                s += '∅'

            s = s.removesuffix(', ') + '\n'

        return s


class UCReachingDefs(UCAnalysis):
    """Reaching definitions analysis"""

    def __init__(self, cfg):
        super().__init__(cfg)

    @property
    def analysis_fn(self):
        def analysis_fn_impl(R, u, v):
            kill_uv = set(self.killset(u, v))
            gen_uv = set(self.genset(u, v))

            rd_u_not_kill_uv = R[u].difference(kill_uv)

            if not rd_u_not_kill_uv.union(gen_uv).issubset(R[v]):
                R[v] = R[v].union(
                    rd_u_not_kill_uv).union(gen_uv)
                return True

            return False

        return analysis_fn_impl

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
        rd = {}

        # Compute initial RD assignments
        for q in self.cfg.nodes:
            if q != self.cfg.source:
                rd[q] = set()

        rd[self.cfg.source] = set(product(self.cfg.vars,
                                          [UCReachingDefs.jolly_node],
                                          [self.cfg.source]))

        # Compute the MFP solution for RD assignments
        ucw = UCWorklist(self.cfg, self.analysis_fn, rd, strategy=UCFIFOStrategy)
        self.iters = ucw.compute()

        if copy:
            return rd

        self.aa = rd

    def __str__(self):
        return super().__str__(
            'RD', lambda aa: f'({str(aa[0])}, {aa[1]}, {aa[2]})')


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
    def analysis_fn(self):
        def analysis_fn_impl(R, u, v):
            kill_uv = set(self.killset(u, v))
            gen_uv = set(self.genset(u, v))

            rd_u_not_kill_uv = R[u].difference(kill_uv)

            if not rd_u_not_kill_uv.union(gen_uv).issubset(R[v]):
                R[v] = R[v].union(
                    rd_u_not_kill_uv).union(gen_uv)
                return True

            return False

        return analysis_fn_impl

    def __genset(self, node, storage):
        if isinstance(node, UCRecordInitializerList):
            self.__genset(node.value[0], storage)
            self.__genset(node.value[1], storage)
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
        elif isinstance(a, UCAExprBinOp):
            self.__genset(a.lhs, storage)
            self.__genset(a.rhs, storage)
        elif isinstance(a, UCCall):
            self.__genset(a.args[0], storage)
        elif isinstance(a, UCNot):
            self.__genset(a.opr.lhs, storage)
            self.__genset(a.opr.rhs, storage)

        return list(set(storage))

    def compute(self, copy=False):
        lv = {}

        # Compute initial LV assignments
        for q in self.cfg.nodes:
            lv[q] = set()

        # Compute the MFP solution for LV assignments
        ucw = UCWorklist(self.cfg, self.analysis_fn, lv, strategy=UCFIFOStrategy)
        self.iters = ucw.compute()

        # Sort LV assignment vales by identifier
        lv = {k: sorted(v, key=lambda v: str(v)) for k, v in lv.items()}

        if copy:
            return lv

        self.aa = lv

    def __str__(self):
        return super().__str__('LV', lambda aa: f'{str(aa)}', forward=False)


class UCDangerousVars(UCAnalysis):
    """UC Dangerous Vars"""

    def __init__(self, cfg):
        super().__init__(cfg)

    @property
    def analysis_fn(self):
        def analysis_fn_impl(R, u, v):
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

        return analysis_fn_impl

    def compute(self, copy=False):
        dv = {}

        # DV=RD for the initial assignment
        rd = UCReachingDefs(self.cfg)
        rd.compute()

        # Lift the assignment to the correct analysis domain
        # and only add initial definitions
        for q, rds in rd.aa.items():
            dv[q] = set()

            for rd_ in rds:
                # Is it an initial definition?
                if rd_[1] == self.jolly_node:
                    dv[q].add(rd_[0])

        # Compute the MFP solution for DV assignments
        ucw = UCWorklist(self.cfg, self.analysis_fn, dv, strategy=UCFIFOStrategy)
        self.iters = rd.iters + ucw.compute()

        if copy:
            return dv

        self.aa = dv

    def __str__(self):
        return super().__str__('DV', lambda dv: f'{str(dv)}')


class UCDetectionSigns(UCAnalysis):
    """Reaching definitions analysis"""

    def __init__(self, cfg):
        super().__init__(cfg)

    @classproperty
    def signs(cls):
        return set(['-', '0', '+'])

    @classproperty
    def bool(cls):
        return set(['tt', 'ff'])

    def __to_abstract_mem(self, vars):
        return { id: self.__to_abstract(var) for id, var in vars.items() }

    def __to_abstract(self, var):
        if isinstance(var, UCRecord):
            return set(
                reduce(set.union, list(
                    map(lambda f: self.get_sign({}, f.value), var.fields)), set())
                )
        elif isinstance(var, UCArray):
            return set(
                reduce(set.union, list(
                    map(lambda v: self.get_sign({}, v), var.value)), set())
                )
        else:
            return self.get_sign({}, var.value)

    def __to_basic_mem(self, mem):
        basic_mems = list()
        mem_, mem_am_ = dict(), dict() # Amalgamated and non- abstract memories

        # Split the abstract memory based on whether the variable type is
        # amalgamated or not
        for var_id, sign in mem.items():
            var = self.cfg.vars[var_id]

            if isinstance(var, UCArray) or isinstance(var, UCRecord):
                if var_id not in mem_am_:
                    mem_am_[var_id] = set()
                mem_am_[var_id] = mem_am_[var_id].union(mem[var_id])
            else:
                if var_id not in mem_:
                    mem_[var_id] = set()
                mem_[var_id] = mem_[var_id].union(mem[var_id])

        sign_product = list(product(*mem_.values()))

        for signs in sign_product:
            basic_mem = {}

            for var_id, sign in zip(mem_.keys(), signs):
                var = self.cfg.vars[var_id]
                basic_mem[var_id] = set([sign])

            basic_mems.append(basic_mem)

        # Merge amalgamated and non- basic memories
        for i in range(len(basic_mems)):
            basic_mems[i] = self.__aa_union(basic_mems[i], mem_am_)

        return basic_mems

    @property
    def initial_mem(self):
        return self.__to_abstract_mem(self.cfg.vars)

    @property
    def empty_mem(self):
        return { id: set() for id, _ in self.cfg.vars.items() }

    def get_sign(self, mem, a):
        assert isinstance(a, UCAExpression)

        def get_sign_aux(mem, a):
            sign = set()

            if isinstance(a, UCAExpression):
                if isinstance(a, UCNumberLiteral):
                    if a.value < 0:
                        sign.add('-')
                    elif a.value == 0:
                        sign.add('0')
                    else:
                        sign.add('+')
                elif isinstance(a, UCRecordInitializerList):
                    sign = set(
                        reduce(set.union, list(
                            map(lambda v: get_sign_aux(mem, v), a.value)), set())
                    )
                elif isinstance(a, UCIdentifier):
                    sign = sign.union(mem[a])
                elif isinstance(a, UCArrayDeref):
                    sign_rhs = get_sign_aux(mem, a.rhs)

                    if sign_rhs.intersection(['0', '+']) != set():
                        sign = sign.union(mem[a.lhs])
                    else:
                        sign = self.empty_mem
                elif isinstance(a, UCRecordDeref):
                    sign = sign.union(mem[a.lhs])
                elif isinstance(a, UCAdd):
                    sign_lhs = get_sign_aux(mem, a.lhs)
                    sign_rhs = get_sign_aux(mem, a.rhs)

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '-' and s2 == '-' or\
                                    s1 == '-' and s2 == '0' or\
                                    s1 == '0' and s2 == '-':
                                sign.add('-')
                            elif s1 == '-' and s2 == '+' or s1 == '+' and s2 == '-':
                                sign = self.signs
                            elif s1 == '0' and s2 == '0':
                                sign.add('0')
                            else:
                                sign.add('+')
                elif isinstance(a, UCSub):
                    sign_lhs = get_sign_aux(mem, a.lhs)
                    sign_rhs = get_sign_aux(mem, a.rhs)

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '-' and s2 == '0' or\
                                    s1 == '-' and s2 == '+' or\
                                    s1 == '0' and s2 == '+':
                                sign.add('-')
                            elif s1 == '+' and s2 == '+' or s1 == '-' and s2 == '-':
                                sign = self.signs
                            elif s1 == '0' and s2 == '0':
                                sign.add('0')
                            else:
                                sign.add('+')
                elif isinstance(a, UCMul):
                    sign_lhs = get_sign_aux(mem, a.lhs)
                    sign_rhs = get_sign_aux(mem, a.rhs)

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '+' and s2 == '-' or\
                                    s1 == '-' and s2 == '+':
                                sign.add('-')
                            elif s1 == '-' and s2 == '-' or\
                                    s1 == '+' and s2 == '+':
                                sign.add('+')
                            else:
                                sign.add('0')
                elif isinstance(a, UCDiv):
                    sign_lhs = get_sign_aux(mem, a.lhs)
                    sign_rhs = get_sign_aux(mem, a.rhs)

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '+' and s2 == '-' or\
                                    s1 == '-' and s2 == '+':
                                sign.add('-')
                            elif s1 == '-' and s2 == '-' or\
                                    s1 == '+' and s2 == '+':
                                sign.add('+')
                            elif s2 == '0':
                                sign = self.empty_mem
                            else:
                                sign.add('0')
                elif isinstance(a, UCMod):
                    # In the modulo operator, the sign is equal to the
                    # sign of the divisor (rhs)
                    sign_lhs = get_sign_aux(mem, a.lhs)
                    sign_rhs = get_sign_aux(mem, a.rhs)

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s2 == '+':
                                sign.add('+')
                            elif s2 == '-':
                                sign.add('-')
                            else: # s2 == '0'
                                sign = self.empty_mem

            return sign

        return get_sign_aux(mem, a)

    def get_bool(self, mem, a):
        assert isinstance(a, UCRExpression) or isinstance(a, UCBExpression)

        def get_bool_aux(mem, a):
            bool = set()

            # UCBExpressions
            if isinstance(a, UCBExpression):
                if isinstance(a, UCBoolLiteral):
                    bool.add('tt' if a.value == True else 'ff')
                elif isinstance(a, UCNot):
                    bool_opr = get_bool_aux(mem, a.opr)

                    for b in bool_opr:
                        if b == 'tt':
                            bool.add('ff')
                        else:
                            bool.add('tt')
                elif isinstance(a, UCAnd):
                    bool_lhs = self.get_bool(mem, a.lhs)
                    bool_rhs = self.get_bool(mem, a.rhs)

                    for b1 in bool_lhs:
                        for b2 in bool_rhs:
                            if b1 == b2 and b1 == 'tt':
                                bool.add('tt')
                            else:
                                bool.add('ff')
                elif isinstance(a, UCOr):
                    bool_lhs = self.get_bool(mem, a.lhs)
                    bool_rhs = self.get_bool(mem, a.rhs)

                    for b1 in bool_lhs:
                        for b2 in bool_rhs:
                            if b1 == 'tt' or b2 == 'tt':
                                bool.add('tt')
                            else:
                                bool.add('ff')
            # UCRExpressions
            else:
                if isinstance(a, UCEq):
                    sign_lhs = self.get_sign(mem, a.lhs)
                    sign_rhs = self.get_sign(mem, a.rhs)

                    exit = False

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '0' and s2 == '0':
                                bool.add('tt')
                            elif s1 != s2:
                                bool.add('ff')
                            else:
                                bool = self.bool
                                exit = True

                                break

                        if exit:
                            break
                elif isinstance(a, UCNeq):
                    sign_lhs = self.get_sign(mem, a.lhs)
                    sign_rhs = self.get_sign(mem, a.rhs)

                    exit = False

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 != s2:
                                bool.add('tt')
                            elif s1 == '0' and s2 == '0':
                                bool.add('ff')
                            else:
                                bool = self.bool
                                exit = True

                                break

                        if exit:
                            break
                elif isinstance(a, UCLt):
                    sign_lhs = self.get_sign(mem, a.lhs)
                    sign_rhs = self.get_sign(mem, a.rhs)

                    exit = False

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '0' and s2 == '+' or\
                                    s1 == '-' and s2 == '+' or\
                                    s1 == '-' and s2 == '0':
                                bool.add('tt')
                            elif s1 == '+' and s2 == '-' or\
                                    s1 == '0' and s2 == '-' or\
                                    s1 == '+' and s2 == '0' or\
                                    s1 == s2 and s1 == '0':
                                bool.add('ff')
                            else:
                                bool = self.bool
                                exit = True

                                break

                        if exit:
                            break
                elif isinstance(a, UCLte):
                    sign_lhs = self.get_sign(mem, a.lhs)
                    sign_rhs = self.get_sign(mem, a.rhs)

                    exit = False

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '0' and s2 == '+' or\
                                    s1 == '-' and s2 == '+' or\
                                    s1 == '-' and s2 == '0' or\
                                    s1 == s2 and s1 == '0':
                                bool.add('tt')
                            elif s1 == '+' and s2 == '-' or\
                                    s1 == '+' and s2 == '0' or\
                                    s1 == '0' and s2 == '-':
                                bool.add('ff')
                            else:
                                bool = self.bool
                                exit = True

                                break

                        if exit:
                            break              
                elif isinstance(a, UCGt):
                    sign_lhs = self.get_sign(mem, a.lhs)
                    sign_rhs = self.get_sign(mem, a.rhs)

                    exit = False

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '+' and s2 == '0' or\
                                    s1 == '+' and s2 == '-' or\
                                    s1 == '0' and s2 == '-':
                                bool.add('tt')
                            elif s1 == '-' and s2 == '+' or\
                                    s1 == '0' and s2 == '+' or\
                                    s1 == '-' and s2 == '0' or\
                                    s1 == s2 and s1 == '0':
                                bool.add('ff')
                            else:
                                bool = self.bool
                                exit = True

                                break

                        if exit:
                            break
                elif isinstance(a, UCGte):
                    sign_lhs = self.get_sign(mem, a.lhs)
                    sign_rhs = self.get_sign(mem, a.rhs)

                    exit = False

                    for s1 in sign_lhs:
                        for s2 in sign_rhs:
                            if s1 == '+' and s2 == '0' or\
                                    s1 == '+' and s2 == '-' or\
                                    s1 == '0' and s2 == '-' or\
                                    s1 == s2 and s1 == '0':
                                bool.add('tt')
                            elif s1 == '-' and s2 == '+' or\
                                    s1 == '-' and s2 == '0' or\
                                    s1 == '0' and s2 == '+':
                                bool.add('ff')
                            else:
                                bool = self.bool
                                exit = True

                                break

                        if exit:
                            break

            return bool

        return get_bool_aux(mem, a)

    def __aa_issubset(self, aa1, aa2):
        """Subset extended for DS analysis domain"""
        if not set(aa1.keys()).issubset(aa2.keys()):
            return False

        for var, sign in aa1.items():
            if var not in aa2 or not sign.issubset(aa2[var]):
                return False

        return True

    def __aa_union(self, aa1, aa2):
        """Union extended for DS analysis domain"""
        aa = aa1.copy()

        for var, sign in aa2.items():
            if var not in aa:
                aa[var] = set()
            aa[var] = aa[var].union(sign)

        return aa

    def __aa_intersection(self, aa1, aa2):
        """Intersection extended for DS analysis domain"""
        aa = aa1.copy()

        for var, sign in aa2.items():
            if var not in aa:
                aa[var] = set()
            aa[var] = aa[var].intersection(sign)

        return aa

    def __aa_complement(self, aa):
        """Complement extended for DS analysis domain"""
        aa_ = aa.copy()

        for var, sign in aa_.items():
            aa_[var] = self.signs.difference(sign)

        return aa_

    @property
    def analysis_fn(self):
        def analysis_fn_impl(R, u, v):
            uv = self.cfg.edges[u, v]
            a = uv['action']

            # TODO: Add support for UCCall
            if isinstance(a, UCAssignment):
                var, sign = a.lhs, self.get_sign(R[u], a.rhs)

                if isinstance(var, UCArrayDeref):
                    var = var.lhs
                elif isinstance(var, UCRecordDeref):
                    var = var.lhs

                if R[u] != self.empty_mem:
                    ru1 = R[u].copy()
                    ru1[var] = sign
                else:
                    ru1 = self.empty_mem

                if not self.__aa_issubset(ru1, R[v]):
                    R[v] = self.__aa_union(ru1, R[v])
                    return True
            elif isinstance(a, UCRExpression) or isinstance(a, UCBExpression):
                basic_mems = self.__to_basic_mem(R[u])

                ru1 = self.empty_mem

                for basic_mem in basic_mems:
                    bool = self.get_bool(basic_mem, a)

                    if 'tt' in bool:
                        ru1 = self.__aa_union(ru1, basic_mem)

                if not self.__aa_issubset(ru1, R[v]):
                    R[v] = self.__aa_union(ru1, R[v])
                    return True

            return False

        return analysis_fn_impl

    def compute(self, copy=False):
        ds = {}

        # Define the initial abstract memory
        mem = self.initial_mem

        # Define the initial DS assignment
        for q in self.cfg.nodes:
            ds[q] = self.empty_mem

        # Define the initial DS assignment for the source node
        ds[self.cfg.source] = mem

        # Compute the MFP solution for DS assignments
        ucw = UCWorklist(self.cfg, self.analysis_fn, ds, strategy=UCFIFOStrategy)
        self.iters = ucw.compute()

        if copy:
            return ds

        self.aa = ds

    def __str__(self):
        return super().__str__('DS', lambda ds: f'{ds[0]}: {ds[1]}')
