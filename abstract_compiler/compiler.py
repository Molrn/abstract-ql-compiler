from abc import abstractmethod, ABC
from typing import Generic, TypeVar, List
from anytree import Node, RenderTree

from . import tokens
from .lexer import Lexer
from .parser import StatementType, Parser

T = TypeVar('T')


class Compiler(ABC, Generic[T]):

    def run(self, statement: str, verbose: bool = False):
        if verbose:
            print(f"\nSTATEMENT\n\n{statement}")
        token_list = Lexer(statement).run()
        if verbose:
            print(f"\nTOKENS\n\n{' '.join([str(token) for token in token_list])}")
        syntax_tree = Parser(token_list).run()
        if verbose:
            print(f"\nSYNTAX TREE\n")
            for pre, _, node in RenderTree(syntax_tree):
                print("%s%s" % (pre, node.name))
        results = self.execute_statement(syntax_tree)
        if verbose:
            print(f"\nRESULTS\n\n{results}")
        return results

    def execute_statement(self, statement_node: Node):
        if statement_node.name == StatementType.SELECT:
            from_node = None
            select_node = None
            for node in statement_node.children:
                token = node.name
                if isinstance(token, tokens.SelectToken):
                    select_node = node
                elif isinstance(token, tokens.FromToken):
                    from_node = node
            if not select_node or not from_node:
                raise ValueError()
            return self.execute_select_statement(select_node, from_node)

    def execute_select_statement(self, select_node: Node, from_node: Node) -> T:
        token = from_node.children[0].name
        if not isinstance(token, tokens.IdentifierToken):
            raise ValueError()
        id_values = token.get_values()
        if isinstance(token, tokens.Depth1IdentifierToken):
            table = self.get_table_from_1_id(id_values[0])
        elif isinstance(token, tokens.Depth2IdentifierToken):
            table = self.get_table_from_2_ids(
                id_values[0], id_values[1]
            )
        elif isinstance(token, tokens.Depth3IdentifierToken):
            table = self.get_table_from_3_ids(
                id_values[0], id_values[1], id_values[2]
            )
        else:
            raise ValueError()

        columns = []
        for node in select_node.children:
            token = node.name
            if not isinstance(token, tokens.Depth1IdentifierToken):
                raise ValueError()
            columns.append(token.get_values()[0])
        return self.select_columns_from_table(table, columns)

    @abstractmethod
    def get_table_from_1_id(self, identifier: str) -> T:
        pass

    @abstractmethod
    def get_table_from_2_ids(self, left_id: str, right_id: str) -> T:
        pass

    @abstractmethod
    def get_table_from_3_ids(
            self, left_id: str, middle_id: str, right_id: str
    ) -> T:
        pass

    @abstractmethod
    def select_columns_from_table(self, table: T, columns: List[str]) -> T:
        pass
