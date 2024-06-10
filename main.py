from anytree import RenderTree

from lexer import Lexer
from parser import Parser

if __name__ == "__main__":
    tokens = Lexer('SELECT "column1" "column2" FROM "schema"."table"').run()
    syntax_tree = Parser(tokens).run()
    for pre, _, node in RenderTree(syntax_tree):
        print("%s%s" % (pre, node.name))
