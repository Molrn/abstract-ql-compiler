from abc import ABC, abstractmethod
from sys import stderr, stdout
from typing import Generic, TypeVar

from anytree import Node, RenderTree

from . import tokens
from .exceptions import CompilationError, LogicalError
from .lexer import Lexer
from .parser import ComposedNodeType, Parser

Table = TypeVar("Table")
Result = TypeVar("Result")


class AbstractCompiler(ABC, Generic[Table, Result]):

    def execute(self, statement: str):
        token_list = Lexer(statement).run()
        syntax_tree = Parser(token_list).run()
        return self._execute_statement(syntax_tree)

    def console_execute(
        self,
        statement: str,
        output_stream=stdout,
        error_stream=stderr,
        verbose=True
    ) -> Result:
        try:
            if verbose:
                output_stream.write(f"STATEMENT\n\n{statement}\n\n")
            token_list = Lexer(statement).run()
            if verbose:
                token_str_list = " ".join([str(token) for token in token_list])
                output_stream.write(f"TOKENS\n\n{token_str_list}\n\n")
            syntax_tree = Parser(token_list).run()
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
        if statement_root.name == ComposedNodeType.SELECT:
            from_node = None
            select_node = None
            for node in statement_root.children:
                token = node.name
                if isinstance(token, tokens.SelectToken):
                    select_node = node
                elif isinstance(token, tokens.FromToken):
                    from_node = node
            if not select_node or not from_node:
                raise LogicalError(
                    "SELECT and FROM tokens expected in Select Statement"
                )
            return self._execute_select_statement(select_node, from_node)

    def _execute_select_statement(
        self, select_node: Node, from_node: Node
    ) -> Result:
        table_id_node = from_node.children[0]
        if table_id_node.name != ComposedNodeType.TABLE_IDENTIFIER:
            raise LogicalError("Table identifier enpected in FROM clause")
        table = self._get_table_id_from_node(table_id_node)
        columns = []
        for node in select_node.children:
            token = node.name
            if not isinstance(token, tokens.IdentifierToken):
                raise LogicalError("Identifier token expected in columns")
            columns.append(token.get_value())
        return self.select_columns_from_table(table, columns)

    def _get_table_id_from_node(self, table_id_node: Node) -> Table:
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
        elif id_count == 3:
            return self.get_table_from_3_ids(
                id_values[0], id_values[1], id_values[2]
            )
        else:
            raise LogicalError("Unrecognized table identifier")

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
