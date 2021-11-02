"""Worklist Algorithm"""

from abc import abstractmethod
from collections import deque

from .dfst import UCSpanTree
from lang.ops import *
from passes.cfg import UCProgramGraph
from utils.decorators import classproperty
from utils.functools import apply

import networkx as nx


class UCWorklistStrategy:
    """Worklist Strategy"""

    def __init__(self, ucw, cfg):
        self._worklist = []
        self._cfg = cfg

    @abstractmethod
    def update(self, x):
        raise NotImplementedError()

    @abstractmethod
    def insert(self, x):
        raise NotImplementedError()

    @abstractmethod
    def extract(self):
        raise NotImplementedError()

    @classproperty
    def node_ordering_fn(cls):
        return nx.dfs_preorder_nodes


class UCFIFOStrategy(UCWorklistStrategy):
    """FIFO (Queue) Strategy"""

    def __init__(self, ucw, cfg):
        super().__init__(ucw, cfg)
        self._worklist = deque(self._worklist)

    def insert(self, x):
        if x is not None:
            self._worklist.append(x)

    def extract(self):
        return self._worklist.popleft()


class UCLIFOStrategy(UCWorklistStrategy):
    """LIFO (Stack) Strategy"""

    def __init__(self, ucw, cfg):
        super().__init__(ucw, cfg)
        self._worklist = deque(self._worklist)

    def insert(self, x):
        if x is not None:
            self._worklist.append(x)

    def extract(self):
        return self._worklist.pop()


class UCRRStrategy(UCWorklistStrategy):
    """Round-robin Strategy"""

    def __init__(self, ucw, cfg):
        super().__init__(ucw, cfg)
        self._worklist = [deque(self._worklist), set()]

    def insert(self, x):
        if x is not None and x not in self._worklist[0]:
            self._worklist[1].add(x)

    def extract(self):
        if len(self._worklist[0]) == 0:
            rp, _ = UCSpanTree.dfs_tree(self._cfg)
            
            for x in set(self._worklist[0]).difference(self._worklist[1]):
                rp.pop(x)

            rp = UCSpanTree.sort_rp(rp)

            self._worklist[0] = deque(rp.keys())
            self._worklist[1] = set()

        return self._worklist[0].popleft()

    @classproperty
    def node_ordering_fn(cls):
        return lambda cfg, source:\
                UCSpanTree.sort_rp(UCSpanTree.dfs_tree(cfg, source)[0]).keys()


class UCWorklist:
    """Worklist Algorithm"""

    def __init__(self, cfg, af, r, strategy=UCLIFOStrategy):
        self.cfg = cfg
        self.af = af
        self.r = r
        self.strategy_type = strategy
        self.strategy = strategy(self, cfg)
        self.worklist = self.strategy._worklist

        # TODO: Refactor by getting the ordered nodes from the strategy directly
        # since it now has access to the CFG
        if cfg.source is not None:
            for q in strategy.node_ordering_fn(cfg, source=cfg.source):
                self.strategy.insert(q)

    @property
    def empty(self):
        return UCWorklist(UCProgramGraph.empty,
                            lambda _: set(), dict(), self.strategy_type)

    def insert(self, x):
        self.strategy.insert(x)

    def extract(self):
        return self.strategy.extract()

    def compute(self):
        iters = 0

        while self != self.empty:
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
