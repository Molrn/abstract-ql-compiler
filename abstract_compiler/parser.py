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
    COLUMN = "COLUMN"
    TABLE = "TABLE"


class Parser:
    def __init__(self, token_list: list[AbstractToken]):
        self.tokens = token_list

    def parse(self) -> Node:
        return self._statement()

    def _peek_next_token(self) -> AbstractToken | None:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def _consume_token(self, token_class: type[AbstractToken]) -> AbstractToken:
        token = self._peek_next_token()
        if token is None:
            eof_locator = LexemeLocator(-1, -1, -1, -1)
            raise SyntacticError(
                "Unexpected end of tokens "
                f"(expected: {token_class.__name__})",
                eof_locator
            )
        if isinstance(token, token_class):
            return self.tokens.pop(0)
        raise SyntacticError(
            f"Unexpected token: {token.lexeme} "
            f"(expected: {token_class.__name__})",
            token.locator
        )

    def _statement(self) -> Node:
        return Node(
            NonTerminalNodeType.SELECT_STATEMENT, children=self._select_statement()
        )

    def _select_statement(self) -> list[Node]:
        return [self._select(), self._from()]

    def _select(self) -> Node:
        select_node = Node(self._consume_token(tokens.SelectToken))
        return Node(
            NonTerminalNodeType.SELECT, 
            children=[select_node, self._column_list()]
        )

    def _column_list(self) -> Node:
        columns = [self._column()]
        while isinstance(self._peek_next_token(), tokens.IdentifierToken):
            columns.append(self._column())
        return Node(NonTerminalNodeType.COLUMN_LIST, children=columns)

    def _column(self) -> Node:
        return Node(
            NonTerminalNodeType.COLUMN,
            children=[Node(self._consume_token(tokens.IdentifierToken))]
        )

    def _from(self) -> Node:
        from_node = Node(self._consume_token(tokens.FromToken))
        return Node(
            NonTerminalNodeType.FROM, children=[from_node, self._table()]
        )

    def _table(self) -> Node:
        table = Node(NonTerminalNodeType.TABLE)
        Node(self._consume_token(tokens.IdentifierToken), parent=table)
        if isinstance(self._peek_next_token(), tokens.DotToken):
            Node(self._consume_token(tokens.DotToken), parent=table)
            Node(self._consume_token(tokens.IdentifierToken), parent=table)
            if isinstance(self._peek_next_token(), tokens.DotToken):
                Node(self._consume_token(tokens.DotToken), parent=table)
                Node(self._consume_token(tokens.IdentifierToken), parent=table)
        return table
