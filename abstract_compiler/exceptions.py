class CompilationError(Exception):
    pass


class SyntacticError(CompilationError):
    pass


class LexicalError(CompilationError):
    pass


class SemanticError(CompilationError):
    pass


class LogicalError(CompilationError):
    pass
