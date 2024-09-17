from anytree import Node

from abstract_compiler.lexeme_locator import LexemeLocator


class CompilationError(Exception):
    def __init__(self, message: str, location: LexemeLocator | None):
        super().__init__(
            message if not location else
            f"{message} at line {location.line_start},"
            f" column {location.column_start}"
        )
        self.location = location


class SyntacticError(CompilationError):
    pass


class LexicalError(CompilationError):
    pass


class SemanticError(CompilationError):
    pass
