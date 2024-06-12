from abc import abstractmethod, ABC
from sys import stdout, stderr
from typing import Generic, TypeVar

from anytree import Node, RenderTree

from . import tokens
from .lexer import Lexer
from .parser import StatementType, Parser

T = TypeVar('T')


class AbstractCompiler(ABC, Generic[T]):

    def __init__(self, output_stream=stdout, error_stream=stderr):
        self.output_stream = output_stream
        self.error_stream = error_stream

    def execute(self, statement: str, verbose: bool = False):
        from abstract_compiler.exceptions import CompilationError
        try:
            if verbose:
                self.output_stream.write(f"STATEMENT\n\n{statement}\n\n")
            token_list = Lexer(statement).run()
            if verbose:
                token_str_list = ' '.join(
                    [str(token) for token in token_list]
                )
                self.output_stream.write(f"\n\nTOKENS\n\n{token_str_list}\n\n")
            syntax_tree = Parser(token_list).run()
            if verbose:
                self.output_stream.write("SYNTAX TREE\n\n")
                for pre, _, node in RenderTree(syntax_tree):
                    self.output_stream.write("%s%s\n" % (pre, node.name))
                self.output_stream.write("\n")
            results = self._execute_statement(syntax_tree)
            if verbose:
                self.output_stream.write("RESULTS\n\n")
                self.display_results(results)
            return results
        except CompilationError as e:
            self.error_stream.write(f"{e}\n")

    def _execute_statement(self, statement_root: Node):
        if statement_root.name == StatementType.SELECT:
            from_node = None
            select_node = None
            for node in statement_root.children:
                token = node.name
                if isinstance(token, tokens.SelectToken):
                    select_node = node
                elif isinstance(token, tokens.FromToken):
                    from_node = node
            if not select_node or not from_node:
                raise ValueError()
            return self._execute_select_statement(select_node, from_node)

    def _execute_select_statement(self, select_node: Node, from_node: Node) -> T:
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
    def display_results(self, results: T):
        pass

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
    def select_columns_from_table(self, table: T, columns: list[str]) -> T:
        pass
