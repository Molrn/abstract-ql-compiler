import re
from abc import ABC, abstractmethod
from enum import StrEnum

from abstract_compiler.lexeme_locator import LexemeLocator


class TokenType(StrEnum):
    SELECT = "SELECT"
    FROM = "FROM"
    ID = "ID"
    DOT = "DOT"
    UNDEFINED = "UNDEFINED"


class AbstractToken(ABC):
    def __init__(self, lexeme: str, locator: LexemeLocator):
        self.locator = locator
        self.lexeme = lexeme

    def is_valid(self) -> bool:
        return not re.fullmatch(self.regular_expression(), self.lexeme) is None

    @property
    @abstractmethod
    def token_type(self) -> TokenType:
        pass

    @abstractmethod
    def regular_expression(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"<{self.token_type}, {self.lexeme}, {self.locator}>"


class ReservedWordToken(AbstractToken, ABC):
    def regular_expression(self) -> str:
        regular_expression = ""
        for char in self.token_type:
            regular_expression += f"[{char.upper()}{char.lower()}]"
        return regular_expression


class SelectToken(ReservedWordToken):
    token_type = TokenType.SELECT


class FromToken(ReservedWordToken):
    token_type = TokenType.FROM


class IdentifierToken(AbstractToken):
    token_type = TokenType.ID

    def regular_expression(self) -> str:
        return '"[^"]*"'

    def get_value(self) -> str:
        return self.lexeme[1:-1]


class DotToken(AbstractToken):
    token_type = TokenType.DOT

    def regular_expression(self) -> str:
        return "\\."
