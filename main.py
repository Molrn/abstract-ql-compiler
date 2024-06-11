import argparse
from dict_compiler import DictCompiler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("statement", type=str)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    results = DictCompiler().run(args.statement, args.verbose)
    if not args.verbose:
        print(results)