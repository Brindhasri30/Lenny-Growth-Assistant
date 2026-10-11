"""
Database initialization and verification CLI script.
Run with:
    python -m app.init_db
from the backend/ directory.
"""
import sys
from sqlalchemy import inspect, text

from app.config import get_settings
from app.database import Base, check_db_connection, get_engine, init_db
from app.logging_config import get_logger

logger = get_logger("init_db")


def main() -> int:
    settings = get_settings()
    print("=" * 60)
    print("Lenny Growth Assistant — Database Initialization")
    print("=" * 60)
    print(f"Target Database URL: {settings.database_url}")
    print()

    # Step 1: Check connection
    print("Step 1: Testing database connection...")
    connected, error = check_db_connection()
    if not connected:
        print("[FAIL] Could not connect to PostgreSQL!")
        print(f"       Error: {error}")
        print()
        print("Troubleshooting steps:")
        print("  1. Verify PostgreSQL is running:")
        print("     In PowerShell (admin) or cmd: net start postgresql-x64-16 (or your version)")
        print("     Or check Windows Services (services.msc) -> 'postgresql'")
        print("  2. Verify the database 'lenny_assistant' exists:")
        print("     psql -U postgres -c \"CREATE DATABASE lenny_assistant;\"")
        print("  3. Check credentials in your .env file:")
        print("     DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/lenny_assistant")
        return 1

    print("[OK]   Database connection successful!")
    print()

    # Step 2: Initialize tables and indices
    print("Step 2: Creating tables and search indices...")
    try:
        init_db()
        print("[OK]   Table creation and FTS indexing completed!")
    except Exception as e:
        print(f"[FAIL] Error initializing database tables: {e}")
        return 1
    print()

    # Step 3: Verify created tables
    print("Step 3: Verifying tables...")
    engine = get_engine()
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    required_tables = [
        "chat_sessions",
        "messages",
        "transcript_sources",
        "transcript_chunks",
        "artifacts",
        "app_config",
    ]

    missing = []
    for tbl in required_tables:
        if tbl in table_names:
            columns = [col["name"] for col in inspector.get_columns(tbl)]
            print(f"  [FOUND] {tbl} ({len(columns)} columns: {', '.join(columns[:5])}...)")
        else:
            missing.append(tbl)
            print(f"  [MISSING] {tbl}")

    if missing:
        print(f"\n[FAIL] Missing tables: {missing}")
        return 1

    # Check FTS index if PostgreSQL
    if engine.dialect.name == "postgresql":
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT indexname FROM pg_indexes 
                    WHERE tablename = 'transcript_chunks' 
                    AND indexname = 'idx_transcript_chunks_fts';
                    """
                )
            ).fetchone()
            if result:
                print("  [FOUND] Full-text search GIN index on transcript_chunks.search_vector")
            else:
                print("  [WARN] Full-text search index not found on transcript_chunks")

    print()
    print("=" * 60)
    print("SUCCESS: Database is fully initialized and verified!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
