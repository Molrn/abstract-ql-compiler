from abstract_compiler.lexeme_locator import LexemeLocator


class CompilationError(Exception):
    def __init__(self, message: str, location: LexemeLocator):
        super().__init__(f'"{message}" {location}')
        self.location = location


class SyntacticError(CompilationError):
    pass


class LexicalError(CompilationError):
    pass


class SemanticError(CompilationError):
    pass
