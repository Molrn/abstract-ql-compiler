from typing import TextIO

from . import tokens
from .exceptions import LexicalError
from .lexeme_locator import LexemeLocator
from .tokens import AbstractToken


class Lexer:
    TOKEN_CLASSES: list[type[AbstractToken]] = [
        tokens.SelectToken,
        tokens.FromToken,
        tokens.IdentifierToken,
        tokens.DotToken,
    ]

    NON_LEXEME_CHARS = ["\n", " ", "\t"]

    CONCATENATED_LEXEME_STARTERS = ["."]

    CONCATENATED_LEXEME_ENDERS = ["."]

    LEXEME_SEPARATORS = NON_LEXEME_CHARS + CONCATENATED_LEXEME_STARTERS

    SEPARATOR_ENCLOSURES = ['"']

    def __init__(self, input_stream: TextIO):
        self.lines = [[*line] for line in input_stream.readlines()]
        if len(self.lines) == 0:
            raise ValueError("Stream can't be empty")
        self.current_line = self.lines[0]
        self.lines.pop(0)
        self.line_count = 1
        self.column_count = 1
        self.lexeme_line_start = 1
        self.lexeme_column_start = 1

    def analyze(self) -> list[AbstractToken]:
        token_list = []
        while not self._is_eof():
            lexeme = self._get_next_lexeme()
            token_list.append(self._get_token(lexeme))
            self._consume_non_lexeme_chars()
        return token_list

    def _get_next_lexeme(self):
        lexeme = ""
        self.lexeme_line_start = self.line_count
        self.lexeme_column_start = self.column_count
        while not self._is_eof():
            char = self._peek_next_char()
            ignore_separators = False
            for ignore_char in self.SEPARATOR_ENCLOSURES:
                if lexeme.count(ignore_char) % 2 == 1:
                    lexeme += self._consume_char()
                    ignore_separators = True
                    continue
            if ignore_separators:
                continue
            if char == "":
                print(self._is_eof())
            if char not in self.LEXEME_SEPARATORS:
                lexeme += self._consume_char()
                continue
            if char in self.CONCATENATED_LEXEME_ENDERS:
                try:
                    self._get_token(lexeme)
                except LexicalError:
                    lexeme += self._consume_char()
                return lexeme
            if lexeme != "":
                return lexeme

        return lexeme

    def _consume_non_lexeme_chars(self):
        while self._peek_next_char() in self.NON_LEXEME_CHARS:
            self._consume_char()

    def _get_token(self, lexeme: str) -> AbstractToken:
        token_locator = LexemeLocator(
            self.lexeme_line_start,
            self.lexeme_column_start,
            self.line_count,
            self.column_count
        )
        for token_class in self.TOKEN_CLASSES:
            token = token_class(lexeme, token_locator)
            if token.is_valid():
                return token
        raise LexicalError(f"No matching token for lexeme '{lexeme}'", token_locator)

    def _consume_char(self):
        if len(self.current_line) > 0:
            self.column_count += 1
            return self.current_line.pop(0)
        if len(self.lines) > 0 and len(self.lines[0]) > 0:
            self.line_count += 1
            self.column_count = 1
            self.current_line = self.lines[0]
            self.lines.pop(0)
            return self.current_line.pop(0)
        return ""

    def _peek_next_char(self):
        if len(self.current_line) > 0:
            return self.current_line[0]
        if len(self.lines) > 0 and len(self.lines[0]) > 0:
            return self.lines[0][0]
        return ""

    def _is_eof(self):
        return len(self.lines) == 0 and len(self.current_line) == 0
