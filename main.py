import argparse
from dict_compiler import DictCompiler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("statement", type=str)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    compiler = DictCompiler(verbose=args.verbose)
    results = compiler.execute(args.statement)
    if not args.verbose:
        compiler.display_results(results)
