from abc import abstractmethod, ABC
from typing import Generic, TypeVar, List
from anytree import Node

import tokens
from parser import StatementType

T = TypeVar('T')


class Compiler(ABC, Generic[T]):
    def __init__(self, syntax_tree: Node):
        self.syntax_tree = syntax_tree

    def run(self):
        if self.syntax_tree.name == StatementType.SELECT:
            from_node = None
            select_node = None
            for node in self.syntax_tree.children:
                token = node.name
                if isinstance(token, tokens.SelectToken):
                    select_node = node
                elif isinstance(token, tokens.FromToken):
                    from_node = node
            if not select_node or not from_node:
                raise ValueError()
            return self.run_select(select_node, from_node)

    def run_select(self, select_node: Node, from_node: Node) -> T:
        token = from_node.children[0].name
        if not isinstance(token, tokens.IdentifierToken):
            raise ValueError()
        id_values = token.get_values()
        if isinstance(token, tokens.Depth1IdentifierToken):
            table = self.get_table_from_1_id(id_values[0])
        elif isinstance(token, tokens.Depth2IdentifierToken):
            table = self.get_table_from_2_ids(
                id_values[0], id_values[1]
            )
        elif isinstance(token, tokens.Depth3IdentifierToken):
            table = self.get_table_from_3_ids(
                id_values[0], id_values[1], id_values[2]
            )
        else:
            raise ValueError()

        columns = []
        for node in select_node.children:
            token = node.name
            if not isinstance(token, tokens.Depth1IdentifierToken):
                raise ValueError()
            columns.append(token.get_values()[0])
        return self.select_columns_from_table(table, columns)

    @abstractmethod
    def get_table_from_1_id(self, identifier: str) -> T:
        pass

    @abstractmethod
    def get_table_from_2_ids(self, left_id: str, right_id: str) -> T:
        pass

    @abstractmethod
    def get_table_from_3_ids(
            self, left_id: str, middle_id: str, right_id: str
    ) -> T:
        pass

    @abstractmethod
    def select_columns_from_table(self, table: T, columns: List[str]) -> T:
        pass
