"""Micro-C Program Analysis"""

import argparse

from networkx.drawing.nx_pydot import to_pydot

from passes.parse import *
from passes.cfg import *

import matplotlib.pyplot as plt
import graphviz as gv

def main():
    parser = argparse.ArgumentParser(description="Micro-C Program Analysis")
    parser.add_argument("--src-file", dest='src_file', type=str, required=True)

    args = vars(parser.parse_args())

    with open(args['src_file'], 'r') as f:
        src = f.read()

        # AST
        ast = parse(src)
        print(ast)

        # CFG (Program Graph)
        cfg = UCProgramGraph()
        cfg = cfg.compute(ast)
        print(cfg)

        # Draw CFG
        for e in cfg.edges(data=True):
            e[2]['label'] = e[2]['action']

        cfg_dot = to_pydot(cfg)
        cfg_dot.set('nodesep', 3)
        cfg_dot.write('graph.dot', prog='dot')
        # nx.drawing.nx_pydot.write_dot(cfg, 'graph.dot')
        gv.render('dot', 'png', 'graph.dot')

if __name__ == "__main__":
    main()
