import argparse
from sys import stdout

from dict_compiler import DictCompiler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("statement_file", type=str)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    compiler = DictCompiler()
    if args.verbose:
        with open(args.statement_file, "r") as file:
            stdout.write(f"STATEMENT\n\n{file.read()}\n\n")
    with open(args.statement_file, "r") as file:
        results = compiler.console_execute(file, verbose=args.verbose)
        if not args.verbose:
            compiler.results_to_str(results)
