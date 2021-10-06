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

    def __init__(self, cfg, af, r, strategy=UCRRStrategy):
        self.cfg = cfg
        self.worklist = list(nx.dfs_preorder_nodes(cfg, source=cfg.source))\
            if cfg.source is not None\
            else []
        self.af = af
        self.r = r
        self.strategy = strategy(self)

    @classproperty
    def empty(cls):
        return UCWorklist(UCProgramGraph.empty, lambda _: set(), dict())

    def insert(self, x):
        self.strategy.insert(x)

    def extract(self):
        return self.strategy.extract()

    def compute(self):
        iters = 0

        while self != UCWorklist.empty:
            w_update_set = set()

            u = self.extract()
            u_post = self.cfg.successors(u)

            for v in u_post:
                if self.af(self.r, u, v):
                    w_update_set.add(v)

            apply(self.insert, w_update_set)

            iters += 1

        return iters

    def __eq__(self, other):
        if isinstance(other, UCWorklist):
            return self.worklist == other.worklist
        return False
