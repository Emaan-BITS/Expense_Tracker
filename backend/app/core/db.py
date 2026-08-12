"""SQLite helpers. No ORM, so every query in this project is one you wrote."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

BASE_DIR = Path(__file__).parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
DEFAULT_DB_PATH = BASE_DIR.parent.parent / "expenses.db"


def db_path() -> Path:
    # Read the env var on every call rather than once at import, so the app
    # can be pointed at a different database file without touching this code.
    return Path(os.environ.get("EXPENSE_DB", DEFAULT_DB_PATH))


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Commits on success, rolls back on error, and always closes.

    sqlite3's own connection context manager handles the transaction but
    leaves the connection open, which leaks handles and keeps a lock on the
    file. Wrapping it means `with get_conn() as conn:` does the whole job.
    """
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row  # lets you write row["amount_cents"]
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite ships with these off
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the tables if they aren't there. Safe to run on every boot."""
    with get_conn() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
