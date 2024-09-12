from enum import StrEnum

from anytree import Node

from . import tokens
from .exceptions import SyntacticError
from .tokens import Token


class ComposedNodeType(StrEnum):
    SELECT = "SELECT"
    TABLE_IDENTIFIER = "TABLE IDENTIFIER"


class Parser:
    def __init__(self, token_list: list[Token]):
        self.tokens = token_list

    def run(self) -> Node:
        return self._statement()

    def _get_current_token(self) -> Token | None:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def _consume_token(self, token_class: type[Token]) -> Token:
        token = self._get_current_token()
        if token is None:
            raise SyntacticError("Unexpected end of tokens")
        if isinstance(token, token_class):
            return self.tokens.pop(0)
        else:
            raise SyntacticError(f"Unexpected token: {token.lexeme}")

    def _statement(self) -> Node:
        if isinstance(self._get_current_token(), tokens.SelectToken):
            return Node(
                ComposedNodeType.SELECT, children=self._select_statement()
            )

    def _select_statement(self) -> list[Node]:
        select_node = Node(self._consume_token(tokens.SelectToken))
        select_node.children = self._column_list()
        from_node = Node(self._consume_token(tokens.FromToken))
        from_node.children = [self._table()]
        return [select_node, from_node]

    def _column_list(self) -> list[Node]:
        columns = [self._column()]
        while isinstance(self._get_current_token(), tokens.IdentifierToken):
            columns.append(self._column())
        return columns

    def _column(self) -> Node:
        return Node(self._consume_token(tokens.IdentifierToken))

    def _table(self) -> Node:
        table = Node(ComposedNodeType.TABLE_IDENTIFIER)
        Node(self._consume_token(tokens.IdentifierToken), parent=table)
        if isinstance(self._get_current_token(), tokens.DotToken):
            Node(self._consume_token(tokens.DotToken), parent=table)
            Node(self._consume_token(tokens.IdentifierToken), parent=table)
            if isinstance(self._get_current_token(), tokens.DotToken):
                Node(self._consume_token(tokens.DotToken), parent=table)
                Node(self._consume_token(tokens.IdentifierToken), parent=table)
        return table
