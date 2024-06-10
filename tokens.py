import re
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import List


class TokenType(StrEnum):
    SELECT = "SELECT"
    FROM = "FROM"
    ID = "ID"
    UNDEFINED = "UNDEFINED"


class Token(ABC):
    def __init__(self, lexeme: str, token_type: TokenType = TokenType.UNDEFINED):
        self.token_type = token_type
        regex = self.regular_expression()
        if not re.fullmatch(regex, lexeme):
            raise ValueError(
                f"Lexeme '{lexeme}' does not match regular expression '{regex}'"
            )
        self.lexeme = lexeme

    def __repr__(self) -> str:
        return f"<{self.token_type}, {self.lexeme}>"

    @abstractmethod
    def regular_expression(self) -> str:
        pass


class ReservedWordToken(Token):

    def __repr__(self):
        return f"<{self.token_type}>"

    def regular_expression(self) -> str:
        regular_expression = ""
        for char in self.token_type:
            regular_expression += f"[{char.upper()}{char.lower()}]"
        return regular_expression


class SelectToken(ReservedWordToken):
    def __init__(self, lexeme):
        super().__init__(lexeme, TokenType.SELECT)


class FromToken(ReservedWordToken):
    def __init__(self, lexeme):
        super().__init__(lexeme, TokenType.FROM)


class IdentifierToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme, TokenType.ID)

    def regular_expression(self) -> str:
        return "\\.".join(['"[^"]*"'] * self.depth())

    def get_values(self) -> List[str]:
        return self.lexeme[1:-1].split('"."')

    @abstractmethod
    def depth(self) -> int:
        pass


class Depth1IdentifierToken(IdentifierToken):
    def depth(self) -> int:
        return 1


class Depth2IdentifierToken(IdentifierToken):
    def depth(self) -> int:
        return 2


class Depth3IdentifierToken(IdentifierToken):
    def depth(self) -> int:
        return 3
