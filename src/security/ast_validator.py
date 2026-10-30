"""
AST-based SQL Safety Validator.
Parses raw SQL queries into an Abstract Syntax Tree (AST) using SQLGlot
to deterministically guarantee read-only execution.
"""

from typing import Set, Type
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

class SQLSecurityError(Exception):
    """Raised when a query violates AST security constraints."""
    pass

class ASTValidator:
    """
    Validates SQL queries against strict read-only AST constraints.
    Enforces:
    1. Valid SQL syntax according to dialect.
    2. Exactly one statement per execution (no query stacking/piggybacking).
    3. Root statement MUST be an exp.Select or exp.Union.
    4. Zero mutation/administrative nodes (DROP, DELETE, UPDATE, INSERT, ALTER, etc.).
    """


    FORBIDDEN_NODES: Set[Type[exp.Expression]] = {
        exp.Drop,
        exp.Delete,
        exp.Update,
        exp.Insert,
        exp.Alter,
        exp.Create,
        exp.Command,
        exp.TruncateTable,
        exp.Pragma,
        exp.Transaction,
        exp.Merge,
    }

    def __init__(self, dialect: str = "sqlite"):
        self.dialect = dialect

    def validate_and_clean(self, raw_sql: str) -> str:
        """
        Validates the SQL query against read-only security policies.
        Returns the normalized SQL query string if safe.
        Raises SQLSecurityError if any policy is violated.
        """

        # strip markdown wrappers and whitespace if LLM emitted ```sql ... ```
        cleaned_sql = self._strip_markdown(raw_sql)

        if not cleaned_sql:
            raise SQLSecurityError("Empty SQL query received.")

        # parse the SQL string into AST expressions
        try:
            parsed_statements = sqlglot.parse(cleaned_sql, read=self.dialect)
        except ParseError as e:
            raise SQLSecurityError(f"SQL Syntax Error: Unable to parse query. Details: {str(e)}")

        # prevent statement stacking (multi-statement injection)
        if len(parsed_statements) == 0:
            raise SQLSecurityError("Query contained no valid SQL statements.")

        if len(parsed_statements) > 1:
            raise SQLSecurityError(
                f"Multi-statement injection detected. Expected 1 statement, found {len(parsed_statements)}."
            )

        root_expression = parsed_statements[0]

        if root_expression is None:
            raise SQLSecurityError(
                f"Multi-statement injection detected. Expected 1 statement, found {len(parsed_statements)}."
            )

        # enforcing read-only root expressions (must be SELECT or UNION of  SELECTs)
        # In SQLGlot, a SELECT query has root type exp.Select, or exp.Union for combined queries    
        if not isinstance(root_expression, (exp.Select, exp.Union)):
            raise SQLSecurityError(
                f"Unauthorized statement type '{root_expression.__class__.__name__}'. Only SELECT queries are permitted."
            )

        for node in root_expression.walk():
            # check if any AST node belongs to forbidden mutation classes
            for forbidden_type in self.FORBIDDEN_NODES:
                if isinstance(node, forbidden_type):
                    raise SQLSecurityError(
                        f"Prohibited SQL operation detected: '{forbidden_type.__name__}'. "
                        "Database mutations and administrative commands are strictly forbidden."
                    )
        # returning standardized SQL dialect string
        return root_expression.sql(dialect=self.dialect)

    @staticmethod
    def _strip_markdown(query: str) -> str:
        """Removes code block ticks and formatting emitted by LLMs."""

        text = query.strip()
        if text.startswith("```"):
            lines = text.splitlines()

            # dropping (```) in begening & ending
            first_line = lines[0].strip()
            last_line = lines[-1].strip()

            if first_line.startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        return text

# global singleton instance
ast_validator = ASTValidator()