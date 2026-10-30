"""
Database Connection Manager,
Read-only connection sandboxing via SQLAlchemy.
"""

from typing import Any, List, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.config import settings

class DatabaseManager:

    def __init__(self, database_url: str = settings.DATABASE_URL):
        self.raw_url = database_url
        self.engine = self._build_engine()

    def _build_engine(self) -> Engine:
        """
        Building a SQLAlchemy engine configured for strictly read-only execution.
        For SQLite, connects via URI mode: ?mode=ro.
        """
        if self.raw_url.startswith("sqlite"):

            # check db file exists or not
            if not settings.db_path.exists():
                raise FileNotFoundError(
                    f"Database not found at {settings.db_path}. Run `python scripts/init_db.py` first."
                )

            # use sqlite read-only URI
            ro_url = f"sqlite:///file:{settings.db_path}?mode=ro&uri=true"
            return create_engine(ro_url, connect_args={"check_same_thread": False})

        # For production Postgres/MySQL, provide read-only user credentials in DATABASE_URL
        return create_engine(self.raw_url)


    def execute_read_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a validated SELECT query and returns records as a list of dicts.
        Raises an OperationalError if any write/mutation operation is attempted.
        """

        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            # Convert SQLAlchemy Row objects into pure Python dictionaries
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return rows

# Global singleton instance
db_manager = DatabaseManager()