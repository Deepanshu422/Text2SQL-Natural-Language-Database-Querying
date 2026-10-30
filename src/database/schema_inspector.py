"""
Dynamic Schema Inspector.
Extracts live table definitions, columns, and foreign key relationships
directly from the database metadata catalog.
"""
from typing import Dict, List, Any
from sqlalchemy import inspect
from src.database.connection import db_manager

class SchemaInspector:

    def __init__(self):
        self.engine = db_manager.engine

    def get_schema_summary(self) -> str:
        """
        Extracts table names, columns with data types, and foreign key relationships.
        Formats them into a compact, high-signal prompt representation.
        """

        inspector = inspect(self.engine)
        tables = inspector.get_table_names()

        schema_lines: List[str] = []

        for table in tables:
            columns = inspector.get_columns(table)
            fks = inspector.get_foreign_keys(table)

            col_defs = [f"{col['name']} ({str(col['type'])})" for col in columns]
            schema_lines.append(f"Table: {table}")
            schema_lines.append(f"  Columns: {','.join(col_defs)} ")

            if fks:
                fk_defs = [
                    f"{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}"
                    for fk in fks
                ]
                schema_lines.append(f" Foreign Keys: {'; '.join(fk_defs)}")

            schema_lines.append("")

        return "\n".join(schema_lines).strip()

schema_inspector = SchemaInspector()

if __name__ == "__main__":

    print("--- DYNAMIC SCHEMA SUMMARY ---")
    print(schema_inspector.get_schema_summary())
    