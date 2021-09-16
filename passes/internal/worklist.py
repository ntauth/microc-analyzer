"""Worklist Algorithm"""

from abc import abstractmethod
from itertools import product

from lang.ops import *

from utils.decorators import classproperty

import networkx as nx


class UCWorklistStrategy:
    """Worklist Strategy"""

    def __init__(self, ucw):
        self._worklist = ucw.worklist
        self._cfg = ucw.cfg

    @abstractmethod
    def update(self, refine=True):
        raise NotImplementedError()

    @property
    def worklist(self):
        return self._worklist


class UCRRStrategy(UCWorklistStrategy):
    """Round-robin Strategy"""

    def __init__(self, ucw):
        super().__init__(ucw)

    def update(self, refine=True):
        w = self.worklist
        wu = w.pop(0)

        if refine:
            w.append(wu)


class UCLIFOStrategy(UCWorklistStrategy):
    """LIFO (Stack) Strategy"""

    def __init__(self, ucw):
        super().__init__(ucw)

    def update(self, refine=True):
        w = self.worklist
        wu = w.pop(0)
        wu_post = self._cfg.out_edges(wu)

        if refine:
            for wu in wu_post:
                w.insert(0, wu)


class UCWorklist:
    """Worklist Algorithm"""

    def __init__(self, cfg, kill, gen, asgn, strategy=UCRRStrategy):
        self.cfg = cfg
        # edge_dfs for the algorithm to be deterministic
        self.worklist = list(nx.edge_dfs(cfg, source=cfg.sources[0]))
        self.kill = kill
        self.gen = gen
        self.asgn = asgn
        self.strategy = strategy(self)

    def compute(self):
        refine_set = set()
        iters = 0

        while len(self.worklist) > 0:
            u, v = self.worklist[0]

            kill_uv = self.kill[(u, v,)]
            gen_uv = self.gen[(u, v,)]

            rd_u_not_kill_uv = self.asgn[u].difference(kill_uv)

            refine = False

            if not rd_u_not_kill_uv.union(gen_uv).issubset(self.asgn[v]):
                self.asgn[v] = self.asgn[v].union(
                    rd_u_not_kill_uv).union(gen_uv)
                refine_set.add((u, v,))

            if (u, v,) in refine_set:
                refine_set.remove((u, v,))
                refine = True

            self.strategy.update(refine)

            iters += 1

        return iters
