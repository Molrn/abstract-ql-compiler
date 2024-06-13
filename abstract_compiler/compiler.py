from abc import abstractmethod, ABC
from sys import stdout, stderr
from typing import Generic, TypeVar

from anytree import Node, RenderTree

from . import tokens
from .exceptions import CompilationError
from .lexer import Lexer
from .parser import StatementType, Parser

Table = TypeVar("Table")
Result = TypeVar("Result")


class AbstractCompiler(ABC, Generic[Table, Result]):

    def __init__(
        self, output_stream=stdout, error_stream=stderr, verbose=True
    ):
        self.output_stream = output_stream
        self.error_stream = error_stream
        self.verbose = verbose

    def execute(self, statement: str):
        try:
            if self.verbose:
                self.output_stream.write(f"STATEMENT\n\n{statement}\n\n")
            token_list = Lexer(statement).run()
            if self.verbose:
                token_str_list = ' '.join(
                    [str(token) for token in token_list]
                )
                self.output_stream.write(f"\n\nTOKENS\n\n{token_str_list}\n\n")
            syntax_tree = Parser(token_list).run()
            if self.verbose:
                self.output_stream.write("SYNTAX TREE\n\n")
                for pre, _, node in RenderTree(syntax_tree):
                    self.output_stream.write("%s%s\n" % (pre, node.name))
                self.output_stream.write("\n")
            results = self._execute_statement(syntax_tree)
            if self.verbose:
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

    def _execute_select_statement(self, select_node: Node, from_node: Node) -> Result:
        token = from_node.children[0].name
        table = self._get_table_id_from_token(token)
        columns = []
        for node in select_node.children:
            token = node.name
            if not isinstance(token, tokens.Depth1IdentifierToken):
                raise ValueError()
            columns.append(token.get_values()[0])
        return self.select_columns_from_table(table, columns)

    def _get_table_id_from_token(
        self, identifier: tokens.IdentifierToken
    ) -> Table:
        id_values = identifier.get_values()
        if isinstance(identifier, tokens.Depth1IdentifierToken):
            return self.get_table_from_1_id(id_values[0])
        elif isinstance(identifier, tokens.Depth2IdentifierToken):
            return self.get_table_from_2_ids(
                id_values[0], id_values[1]
            )
        elif isinstance(identifier, tokens.Depth3IdentifierToken):
            return self.get_table_from_3_ids(
                id_values[0], id_values[1], id_values[2]
            )
        else:
            raise ValueError(f"Unknown identifier token {identifier}")

    @abstractmethod
    def display_results(self, results: Result):
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
