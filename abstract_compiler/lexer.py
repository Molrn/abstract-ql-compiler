from . import tokens
from .exceptions import LexicalError
from .tokens import Token


class Lexer:
    TOKEN_CLASSES: list[type[Token]] = [
        tokens.SelectToken,
        tokens.FromToken,
        tokens.IdentifierToken,
        tokens.DotToken,
    ]

    NON_LEXEME_CHARS = ['\n', ' ', '\t']

    CONCATENATED_LEXEME_STARTERS = ['.']

    CONCATENATED_LEXEME_ENDERS = ['.']

    LEXEME_SEPARATORS = NON_LEXEME_CHARS + CONCATENATED_LEXEME_STARTERS

    SEPARATOR_ENCLOSURES = ['"']

    def __init__(self, input_text: str):
        self.char_list = [*input_text]
        self.current_lexeme = ""
        self.token_list: list[Token] = []

    def run(self) -> list[Token]:
        while len(self.char_list) > 0:
            lexeme = self._get_next_lexeme()
            self.token_list.append(self._get_token(lexeme))
            self._consume_non_lexeme_chars()
        return self.token_list

    def _get_next_lexeme(self):
        lexeme = ""
        while len(self.char_list) > 0:
            char = self.char_list[0]
            print(char)
            ignore_separators = False
            for ignore_char in self.SEPARATOR_ENCLOSURES:
                if lexeme.count(ignore_char) % 2 == 1:
                    lexeme += self.char_list.pop(0)
                    ignore_separators = True
                    continue
            if ignore_separators:
                continue
            if char not in self.LEXEME_SEPARATORS:
                lexeme += self.char_list.pop(0)
                continue
            if char in self.CONCATENATED_LEXEME_ENDERS:
                try:
                    self._get_token(lexeme)
                except LexicalError:
                    lexeme += self.char_list.pop(0)
                return lexeme
            if lexeme != "":
                return lexeme

        return lexeme

    def _consume_non_lexeme_chars(self):
        while (
            len(self.char_list) > 0 and self.char_list[0]
            in self.NON_LEXEME_CHARS
        ):
            self.char_list.pop(0)

    def _get_token(self, lexeme: str) -> Token:
        for token_class in self.TOKEN_CLASSES:
            try:
                return token_class(lexeme)
            except ValueError:
                pass
        raise LexicalError(f"No matching token for lexeme '{lexeme}'")
