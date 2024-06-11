from typing import List, Type

from . import tokens
from .exceptions import LexicalError
from .tokens import Token


class Lexer:
    TOKEN_CLASSES: List[Type[Token]] = [
        tokens.SelectToken,
        tokens.FromToken,
        tokens.Depth1IdentifierToken,
        tokens.Depth2IdentifierToken,
        tokens.Depth3IdentifierToken,
    ]

    LEXEME_SEPARATORS = ['\n', ' ', '\t']

    SEPARATOR_ENCLOSURES = ['"']

    def __init__(self, input_text: str):
        self.char_list = [*input_text]
        self.current_lexeme = ""
        self.token_list: List[Token] = []

    def run(self) -> List[Token]:
        while len(self.char_list) > 0:
            lexeme = self.get_next_lexeme()
            self.token_list.append(self.get_token(lexeme))
            self.consume_separators()
        return self.token_list

    def get_next_lexeme(self):
        lexeme = ""
        while len(self.char_list) > 0:
            char = self.char_list[0]
            if char not in self.LEXEME_SEPARATORS:
                lexeme += self.char_list.pop(0)
                continue
            else:
                stop_lexeme = True
                for ignore_char in self.SEPARATOR_ENCLOSURES:
                    if lexeme.count(ignore_char) % 2 == 1:
                        lexeme += self.char_list.pop(0)
                        stop_lexeme = False
                if stop_lexeme and lexeme != "":
                    return lexeme
        return lexeme

    def consume_separators(self):
        while len(self.char_list) > 0 and self.char_list[0] in self.LEXEME_SEPARATORS:
            self.char_list.pop(0)

    def get_token(self, lexeme: str) -> Token:
        for token_class in self.TOKEN_CLASSES:
            try:
                return token_class(lexeme)
            except ValueError:
                pass
        raise LexicalError(f"No matching token for lexeme '{lexeme}'")