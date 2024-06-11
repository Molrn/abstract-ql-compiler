import json
from typing import List

from abstract_compiler import Compiler
from abstract_compiler.exceptions import SemanticError


class DictCompiler(Compiler[dict]):

    def __init__(self, data_file_path: str = "dict_compiler/data.json"):
        with open(data_file_path) as file:
            self.data: dict = json.load(file)

    def get_table_from_1_id(self, identifier: str) -> dict:
        schema_databases = []
        for database in self.data.keys():
            for schema in self.data[database].keys():
                if identifier in self.data[database][schema].keys():
                    schema_databases.append((database, schema))
        if len(schema_databases) == 0:
            raise SemanticError(f"Unknown table '{identifier}'")
        if len(schema_databases) > 1:
            raise SemanticError(
                f"Multiple tables with name '{identifier}'.\n"
                "Schema name must be provided"
            )
        (database, schema) = schema_databases[0]
        return self.data[database][schema][identifier]

    def get_table_from_2_ids(self, left_id: str, right_id: str) -> dict:
        databases = []
        for database in self.data.keys():
            if left_id in self.data[database].keys():
                databases.append(database)
        if len(databases) == 0:
            raise SemanticError(f"Unknown schema '{left_id}'")
        if len(databases) > 1:
            raise SemanticError(
                f"Multiple schemas with name '{left_id}'.\n"
                "Database name must be provided"
            )
        schema = self.data[databases[0]][left_id]
        if right_id not in schema.keys():
            raise SemanticError(
                f"Unknown table '{right_id}' in schema '{left_id}'"
            )
        return schema[right_id]

    def get_table_from_3_ids(
            self, left_id: str, middle_id: str, right_id: str
    ) -> dict:
        if left_id not in self.data.keys():
            raise SemanticError(f"Unknown database '{left_id}'")
        if middle_id not in self.data[left_id].keys():
            raise SemanticError(
                f"Unknown schema '{middle_id}' in database '{left_id}'"
            )
        if right_id not in self.data[left_id][middle_id].keys():
            raise SemanticError(
                f"Unknown table '{right_id}' in schema "
                f"'{middle_id}' of database '{left_id}'"
            )
        return self.data[left_id][middle_id][right_id]

    def select_columns_from_table(self, table: dict, columns: List[str]) -> dict:
        selected = []
        for record in table:
            row = {}
            for column in columns:
                if column not in record.keys():
                    raise SemanticError(f"Unknown column '{column}'")
                row[column] = record[column]
            selected.append(row)
        return selected

