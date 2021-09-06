"""Micro-C Program Analysis"""

import argparse

from passes.parse import *
from passes.cfg import *
from passes.analysis import *


def main():
    parser = argparse.ArgumentParser(description="Micro-C Program Analysis")
    parser.add_argument("--src-file", dest='src_file', type=str, required=True)

    args = vars(parser.parse_args())

    with open(args['src_file'], 'r') as f:
        src = f.read()

        # AST
        ast = parse(src)

        # CFG (Program Graph)
        cfg = UCProgramGraph()
        cfg = cfg.compute(ast)
        print(cfg)

        # Draw CFG
        cfg.draw(args['src_file'])

        # Reaching Definitions analysis
        rd = UCReachingDefs(cfg)
        successors = list(cfg.successors(cfg.sources_keys[1]))
        print(successors)
        print(rd.killset(cfg.sources_keys[1], successors[0]))

if __name__ == "__main__":
    main()
