"""
Unit Tests for AST Safety Validator.
Verifies read-only enforcement, statement-stacking prevention, and DDL/DML blocking.
"""

import unittest
import sys
from pathlib import Path

# project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.security.ast_validator import ast_validator, SQLSecurityError

class TestASTValidator(unittest.TestCase):

    def test_valid_simple_select(self):
        """Standard SELECT queries should pass cleanly."""
        query = "SELECT name, country FROM organizations WHERE country = 'India';"
        cleaned = ast_validator.validate_and_clean(query)
        self.assertIn("organizations", cleaned)
        self.assertIn("India", cleaned)

    def test_valid_complex_join_and_aggregation(self):
        """Multi-table JOINs, GROUP BY, and aggregations should pass."""
        query = """
        SELECT o.name, SUM(i.amount_usd) AS total_revenue
        FROM organizations o
        JOIN invoices i ON o.org_id = i.org_id
        WHERE i.status = 'paid'
        GROUP BY o.name
        ORDER BY total_revenue DESC
        LIMIT 5;
        """
        cleaned = ast_validator.validate_and_clean(query)
        self.assertTrue(cleaned.upper().startswith("SELECT"))

    def test_false_positive_prevention(self):
        """
        Crucial Test: Forbidden keywords inside string literals or column aliases
        must NOT trigger security errors.
        """
        # 'Drop' inside literal
        query1 = "SELECT * FROM organizations WHERE name = 'Dropbox Cloud Services';"
        cleaned1 = ast_validator.validate_and_clean(query1)
        self.assertIn("Dropbox Cloud Services", cleaned1)

        # 'delete' inside an alias
        query2 = "SELECT count AS deleted_count FROM invoices;"
        cleaned2 = ast_validator.validate_and_clean(query2)
        self.assertIn("deleted_count", cleaned2)

    def test_blocks_direct_drop_table(self):
        """Direct DDL operations must be rejected."""
        query = "DROP TABLE organizations;"
        with self.assertRaises(SQLSecurityError) as ctx:
            ast_validator.validate_and_clean(query)
        self.assertIn("Unauthorized statement type", str(ctx.exception))

    def test_blocks_direct_delete(self):
        """Direct DML operations must be rejected."""
        query = "DELETE FROM invoices WHERE amount_usd < 100;"
        with self.assertRaises(SQLSecurityError) as ctx:
            ast_validator.validate_and_clean(query)
        self.assertIn("Unauthorized statement type", str(ctx.exception))

    def test_blocks_direct_update_and_insert(self):
        """Mutation queries must be rejected."""
        with self.assertRaises(SQLSecurityError):
            ast_validator.validate_and_clean("UPDATE plans SET monthly_rate_usd = 0;")
        
        with self.assertRaises(SQLSecurityError):
            ast_validator.validate_and_clean("INSERT INTO plans VALUES ('p', 'Free', 0, 100);")

    def test_blocks_multi_statement_injection(self):
        """Piggybacked attacks (stacked queries) must be rejected."""
        query = "SELECT * FROM organizations; DROP TABLE subscriptions;"
        with self.assertRaises(SQLSecurityError) as ctx:
            ast_validator.validate_and_clean(query)
        self.assertIn("Multi-statement injection detected", str(ctx.exception))

    def test_handles_markdown_wrapped_sql(self):
        """LLM-style markdown code fence outputs should be cleaned and accepted."""
        query = """```sql
        SELECT plan_name, monthly_rate_usd FROM plans;
        ```"""
        cleaned = ast_validator.validate_and_clean(query)
        self.assertNotIn("```", cleaned)
        self.assertTrue(cleaned.upper().startswith("SELECT"))


if __name__ == "__main__":
    unittest.main()