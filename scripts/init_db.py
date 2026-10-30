"""
Database Initializer Script.
Reads seed_data.sql and populates the SQLite database using SQLAlchemy.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import settings

def init_database() -> None:
    print(f"[*] Initializing database at: {settings.db_path}")

    # ensure parent directory exists
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)

    # standard read-write connection strictly for migrations/seeding
    engine = create_engine(settings.DATABASE_URL)

    with open(settings.seed_sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # SQLite executes individual statements; split by semicolon
    statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))

    print("[+] Database successfully seeded with enterprise schema and initial data.")


if __name__ == "__main__":
    init_database()