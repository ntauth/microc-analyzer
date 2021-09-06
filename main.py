"""Micro-C Program Analysis"""

import argparse

from passes.parse import *
from passes.cfg import *


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

if __name__ == "__main__":
    main()
