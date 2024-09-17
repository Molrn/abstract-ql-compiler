class LexemeLocator:
    def __init__(
        self,
        line_start: int,
        column_start: int,
        line_end: int,
        column_end: int,
    ):
        self.line_start = self._validate_index(line_start)
        self.column_start = self._validate_index(column_start)
        self.line_end = self._validate_index(line_end)
        self.column_end = self._validate_index(column_end)

    @staticmethod
    def _validate_index(value: int):
        if value < -1:
            raise ValueError(f"invalid index '{value}'")
        return value

    def __repr__(self) -> str:
        if self.line_start == self.line_end:
            return (
                f"at line {self.line_start} from column "
                f"{self.column_start} to column {self.column_end}"
            )
        return (
            f"from line {self.line_start}, column {self.column_start} "
            f"to line {self.line_end}, column {self.column_end}"
        )
