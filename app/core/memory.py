import json
import os
import sqlite3
from pathlib import Path


DB_PATH = Path(
    os.getenv("BLAY_DB_PATH", "data/blay.db")
)


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                instruction TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id)
                    REFERENCES projects(project_id)
                    ON DELETE CASCADE
            )
        """)


def save_plan(plan, event_type=None, details=None):
    init_db()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO projects (
                project_id, status, instruction, data
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                status = excluded.status,
                instruction = excluded.instruction,
                data = excluded.data,
                updated_at = CURRENT_TIMESTAMP
        """, (
            plan["project_id"],
            plan["status"],
            plan["instruction"],
            json.dumps(plan, ensure_ascii=False)
        ))

        if event_type:
            conn.execute("""
                INSERT INTO memory_events (
                    project_id, event_type, details
                )
                VALUES (?, ?, ?)
            """, (
                plan["project_id"],
                event_type,
                json.dumps(details or {}, ensure_ascii=False)
            ))


def get_plan(project_id):
    init_db()

    with get_connection() as conn:
        row = conn.execute("""
            SELECT data FROM projects
            WHERE project_id = ?
        """, (project_id,)).fetchone()

    if row is None:
        return None

    return json.loads(row["data"])


def get_project_events(project_id):
    init_db()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT event_type, details, created_at
            FROM memory_events
            WHERE project_id = ?
            ORDER BY id ASC
        """, (project_id,)).fetchall()

    return [
        {
            "event_type": row["event_type"],
            "details": json.loads(row["details"] or "{}"),
            "created_at": row["created_at"]
        }
        for row in rows
    ]
