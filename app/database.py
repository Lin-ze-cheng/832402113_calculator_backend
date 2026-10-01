"""SQLite persistence for calculation history."""

import os
import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "calculator.db"


def get_database_path() -> Path:
    """Read the database path from the environment or use the project default."""
    configured = os.getenv("CALCULATOR_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DATABASE_PATH


def connect() -> sqlite3.Connection:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def create_history(expression: str, result: str, created_at: str) -> dict[str, Any]:
    with connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO calculation_history (expression, result, created_at)
            VALUES (?, ?, ?)
            """,
            (expression, result, created_at),
        )
        record_id = cursor.lastrowid
    return {
        "id": record_id,
        "expression": expression,
        "result": result,
        "created_at": created_at,
    }


def list_history(limit: int = 100) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 500))
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, expression, result, created_at
            FROM calculation_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_history(record_id: int) -> bool:
    with connect() as connection:
        cursor = connection.execute(
            "DELETE FROM calculation_history WHERE id = ?",
            (record_id,),
        )
    return cursor.rowcount > 0


def clear_history() -> int:
    with connect() as connection:
        cursor = connection.execute("DELETE FROM calculation_history")
    return cursor.rowcount

