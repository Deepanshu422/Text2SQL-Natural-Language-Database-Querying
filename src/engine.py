"""
Text2SQL Defensive Engine Orchestrator.
"""
from typing import Optional
from pydantic import BaseModel

from src.database.schema_inspector import schema_inspector
from src.database.connection import db_manager
from src.security.sanitizer import sql_sanitizer
from src.security.ast_validator import ast_validator, SQLSecurityError

# IMPORT THE NEW EXPLICIT FUNCTIONS
from src.chains.sql_generator import get_sql_generation_chain
from src.chains.nl_synthesizer import get_nl_synthesis_chain 

class Text2SQLResponse(BaseModel):
    success: bool
    question: str
    generated_sql: Optional[str] = None
    sanitized_sql: Optional[str] = None
    raw_results: Optional[list] = None
    answer: str
    error: Optional[str] = None

class Text2SQLEngine:
    def __init__(self):
        self.inspector = schema_inspector
        self.db = db_manager
        self.sanitizer = sql_sanitizer
        self.validator = ast_validator

    def query(self, question: str) -> Text2SQLResponse:
        # Stage 1: Dynamic Schema Inspection
        schema_summary = self.inspector.get_schema_summary()

        # Stage 2: Direct SQL Generation
        try:
            raw_sql = get_sql_generation_chain(schema_summary, question)
        except Exception as e:
            return Text2SQLResponse(
                success=False,
                question=question,
                answer="Failed to generate SQL from the question.",
                error=f"LLM Generation Error: {str(e)}",
            )

        # Stage 3: Sanitization & Deterministic AST Validation
        sanitized_sql = self.sanitizer.sanitize(raw_sql)
        try:
            validated_sql = self.validator.validate_and_clean(sanitized_sql)
        except SQLSecurityError as sec_err:
            return Text2SQLResponse(
                success=False,
                question=question,
                generated_sql=raw_sql,
                sanitized_sql=sanitized_sql,
                answer="Execution blocked: The generated query violated security safety rules.",
                error=f"Security Validation Violation: {str(sec_err)}",
            )

        # Stage 4: Read-Only Database Execution
        try:
            raw_records = self.db.execute_read_query(validated_sql)
        except Exception as db_err:
            return Text2SQLResponse(
                success=False,
                question=question,
                generated_sql=raw_sql,
                sanitized_sql=validated_sql,
                answer="Database query failed during execution.",
                error=f"Database Execution Error: {str(db_err)}",
            )

        # Stage 5: Natural Language Synthesis
        try:
            business_answer = get_nl_synthesis_chain(question, validated_sql, raw_records)
        except Exception as syn_err:
            business_answer = f"Found {len(raw_records)} records matching your query."

        return Text2SQLResponse(
            success=True,
            question=question,
            generated_sql=raw_sql,
            sanitized_sql=validated_sql,
            raw_results=raw_records,
            answer=business_answer,
            error=None,
        )

text2sql_engine = Text2SQLEngine()