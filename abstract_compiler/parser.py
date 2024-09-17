from enum import StrEnum

from anytree import Node

from . import tokens
from .exceptions import SyntacticError
from .lexeme_locator import LexemeLocator
from .tokens import AbstractToken


class NonTerminalNodeType(StrEnum):
    SELECT_STATEMENT = "SELECT STATEMENT"
    SELECT = "SELECT"
    FROM = "FROM"
    COLUMN_LIST = "COLUMN LIST"
    TABLE = "TABLE"


class Parser:
    def __init__(self, token_list: list[AbstractToken]):
        self.tokens = token_list
        self.current_node = None
        self.previous_node = None
        self.syntax_tree = None

    def parse(self) -> Node:
        return self._statement()

    def _peek_next_token(self) -> AbstractToken | None:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def _consume_token(self, token_class: type[AbstractToken]) -> AbstractToken:
        token = self._peek_next_token()
        if token is None:
            raise SyntacticError(
                "Unexpected end of tokens",
                LexemeLocator(-1, -1, -1, -1),
            )
        if isinstance(token, token_class):
            return self.tokens.pop(0)
        raise SyntacticError(
            f"Unexpected token: {token.lexeme} "
            f"(expected: {token_class.__name__})",
            token.locator,
        )

    def _set_current_node(self, node: Node):
        self.previous_node = self.current_node
        self.current_node = node

    def _statement(self) -> Node:
        return self._select_statement()

    def _select_statement(self) -> Node:
        statement_node = Node(NonTerminalNodeType.SELECT_STATEMENT)
        self.syntax_tree = statement_node
        self._set_current_node(statement_node)
        statement_node.children = [self._from()]
        statement_node.children += (self._select(),)
        return statement_node

    def _from(self) -> Node:
        from_node = Node(NonTerminalNodeType.FROM)
        self._set_current_node(from_node)
        from_node.children = [
            Node(self._consume_token(tokens.FromToken)), self._table()
        ]
        return from_node

    def _table(self) -> Node:
        table = Node(NonTerminalNodeType.TABLE)
        self._set_current_node(table)
        Node(self._consume_token(tokens.IdentifierToken), parent=table)
        if isinstance(self._peek_next_token(), tokens.DotToken):
            Node(self._consume_token(tokens.DotToken), parent=table)
            Node(self._consume_token(tokens.IdentifierToken), parent=table)
            if isinstance(self._peek_next_token(), tokens.DotToken):
                Node(self._consume_token(tokens.DotToken), parent=table)
                Node(self._consume_token(tokens.IdentifierToken), parent=table)
        return table

    def _select(self) -> Node:
        select_node = Node(NonTerminalNodeType.SELECT)
        self._set_current_node(select_node)
        select_node.children = [
            Node(self._consume_token(tokens.SelectToken)),
            self._column_list()
        ]
        return select_node

    def _column_list(self) -> Node:
        column_list_node = Node(NonTerminalNodeType.COLUMN_LIST)
        self._set_current_node(column_list_node)
        columns = [Node(self._consume_token(tokens.IdentifierToken))]
        while isinstance(self._peek_next_token(), tokens.IdentifierToken):
            columns.append(Node(self._consume_token(tokens.IdentifierToken)))
        column_list_node.children = columns
        return column_list_node
