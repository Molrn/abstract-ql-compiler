from abc import ABC, abstractmethod
from sys import stderr, stdout
from typing import Generic, TypeVar, TextIO

from anytree import Node, RenderTree

from . import tokens
from .exceptions import CompilationError
from .lexer import Lexer
from .parser import Parser

Table = TypeVar("Table")
Result = TypeVar("Result")


class AbstractCompiler(ABC, Generic[Table, Result]):

    def execute(self, statement: TextIO):
        token_list = Lexer(statement).analyze()
        syntax_tree = Parser(token_list).parse()
        return self._execute_statement(syntax_tree)

    def console_execute(
        self,
        statement: TextIO,
        output_stream=stdout,
        error_stream=stderr,
        verbose=True
    ) -> Result:
        try:
            token_list = Lexer(statement).analyze()
            if verbose:
                token_str_list = " ".join([str(token) for token in token_list])
                output_stream.write(f"TOKENS\n\n{token_str_list}\n\n")
            syntax_tree = Parser(token_list).parse()

            if verbose:
                output_stream.write("SYNTAX TREE\n\n")
                for pre, _, node in RenderTree(syntax_tree):
                    output_stream.write("%s%s\n" % (pre, node.name))
                output_stream.write("\n")
            results = self._execute_statement(syntax_tree)
            if verbose:
                output_stream.write("RESULTS\n\n")
                output_stream.write(
                    self.results_to_str(results)
                )
            return results
        except CompilationError as e:
            error_stream.write(f"{e}\n")

    def _execute_statement(self, statement_root: Node) -> Result:
        select_node = statement_root.children[0]
        from_node = statement_root.children[1]

        table_node = from_node.children[1]
        table = self._get_table_from_node(table_node)

        columns = []
        column_list_node = select_node.children[1]
        for column_node in column_list_node.children:
            token_node = column_node.children[0]
            token = token_node.name
            columns.append(token.get_value())
        return self.select_columns_from_table(table, columns)

    def _get_table_from_node(self, table_id_node: Node) -> Table:
        id_values = []
        for child in table_id_node.children:
            token = child.name
            if isinstance(token, tokens.IdentifierToken):
                id_values.append(token.get_value())

        id_count = len(id_values)
        if id_count == 1:
            return self.get_table_from_1_id(id_values[0])
        elif id_count == 2:
            return self.get_table_from_2_ids(id_values[0], id_values[1])
        else:
            return self.get_table_from_3_ids(
                id_values[0], id_values[1], id_values[2]
            )

    @abstractmethod
    def results_to_str(self, results: Result):
        pass

    @abstractmethod
    def get_table_from_1_id(self, identifier: str) -> Table:
        pass

    @abstractmethod
    def get_table_from_2_ids(self, left_id: str, right_id: str) -> Table:
        pass

    @abstractmethod
    def get_table_from_3_ids(
        self, left_id: str, middle_id: str, right_id: str
    ) -> Table:
        pass

    @abstractmethod
    def select_columns_from_table(
        self, table: Table, columns: list[str]
    ) -> Result:
        pass
