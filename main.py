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
        print(ast)

        # CFG (Program Graph)
        cfg = UCProgramGraph()
        cfg = cfg.compute(ast)

        # Draw CFG
        cfg.draw(args['src_file'])
        print(cfg)

        # RD analysis
        rd = UCReachingDefs(cfg)
        rd.compute()

        # Print RD assignments
        print(rd)

        # LV analysis
        lv = UCLiveVars(cfg)
        lv.compute()

        # Print LV assignments
        print(lv)

        # DV analysis
        dv = UCDangerousVars(cfg)
        dv.compute()

        # Print DV assignments
        print(dv)


if __name__ == "__main__":
    main()
