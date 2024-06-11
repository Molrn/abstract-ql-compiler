from enum import StrEnum
from typing import List, Type
from anytree import Node

from . import tokens
from .tokens import Token


class StatementType(StrEnum):
    SELECT = "SELECT"


class Parser:
    def __init__(self, token_list: List[Token]):
        self.tokens = token_list

    def get_current_token(self) -> Token:
        if len(self.tokens) == 0:
            raise SyntaxError("Unexpected end of tokens")
        return self.tokens[0]

    def consume_token(self, token_class: Type[Token]) -> Token:
        token = self.get_current_token()
        if isinstance(token, token_class):
            return self.tokens.pop(0)
        else:
            raise SyntaxError(f"Unexpected token: {token.lexeme}")

    def run(self) -> Node:
        return self.statement()

    def statement(self) -> Node:
        if isinstance(self.get_current_token(), tokens.SelectToken):
            return Node(
                StatementType.SELECT, children=self.select_statement()
            )

    def select_statement(self) -> List[Node]:
        select_node = Node(self.consume_token(tokens.SelectToken))
        select_node.children = self.column_list()
        from_node = Node(self.consume_token(tokens.FromToken))
        from_node.children = [self.table()]
        return [select_node, from_node]

    def column_list(self) -> List[Node]:
        columns = [self.column()]
        while isinstance(self.get_current_token(), tokens.Depth1IdentifierToken):
            columns.append(self.column())
        return columns

    def column(self) -> Node:
        return Node(self.consume_token(tokens.Depth1IdentifierToken))

    def table(self) -> Node:
        return Node(self.consume_token(tokens.IdentifierToken))
