"""Worklist Algorithm"""

from abc import abstractmethod

from passes.cfg import UCProgramGraph
from lang.ops import *
from utils.decorators import classproperty
from utils.functools import apply

import networkx as nx


class UCWorklistStrategy:
    """Worklist Strategy"""

    def __init__(self, ucw):
        self._worklist = ucw.worklist

    @abstractmethod
    def update(self, x):
        raise NotImplementedError()

    @abstractmethod
    def insert(self, x):
        raise NotImplementedError()

    @abstractmethod
    def extract(self):
        raise NotImplementedError()


class UCRRStrategy(UCWorklistStrategy):
    """Round-robin Strategy"""

    def __init__(self, ucw):
        super().__init__(ucw)

    def insert(self, x):
        if x is not None:
            self._worklist.append(x)

    def extract(self):
        return self._worklist.pop(0)


class UCLIFOStrategy(UCWorklistStrategy):
    """LIFO (Stack) Strategy"""

    def __init__(self, ucw):
        super().__init__(ucw)

    def insert(self, x):
        if x is not None:
            self._worklist.insert(0, x)

    def extract(self):
        return self._worklist.pop(0)


class UCWorklist:
    """Worklist Algorithm"""

    def __init__(self, cfg, kill, gen, asgn, strategy=UCRRStrategy):
        self.cfg = cfg
        self.worklist = list(nx.dfs_preorder_nodes(cfg, source=cfg.source))\
            if cfg.source is not None\
            else []
        self.kill = kill
        self.gen = gen
        self.asgn = asgn
        self.strategy = strategy(self)

    @classproperty
    def empty(cls):
        return UCWorklist(UCProgramGraph.empty, set(), set(), dict())

    def insert(self, x):
        self.strategy.insert(x)

    def extract(self):
        return self.strategy.extract()

    def compute(self, op=lambda x, y: set.union(x, y)):
        iters = 0

        while self != UCWorklist.empty:
            insert_set = set()

            u = self.extract()
            u_post = self.cfg.successors(u)

            for v in u_post:
                kill_uv = self.kill[(u, v,)]
                gen_uv = self.gen[(u, v,)]

                rd_u_not_kill_uv = self.asgn[u].difference(kill_uv)

                r1 = op(rd_u_not_kill_uv, gen_uv)

                if not r1.issubset(self.asgn[v]):
                    self.asgn[v] = self.asgn[v].union(r1)
                    insert_set.add(v)

            apply(self.insert, insert_set)

            iters += 1

        return iters

    def __eq__(self, other):
        if isinstance(other, UCWorklist):
            return self.worklist == other.worklist
        return False
