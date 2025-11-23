"""
Database connection utilities
"""
import sqlite3
from contextlib import contextmanager

DATABASE_PATH = 'database/clinical_ehr.db'

def get_db():
    """Connect to database with Row factory and WAL mode"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

@contextmanager
def get_db_context():
    """Context manager for database connection"""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
