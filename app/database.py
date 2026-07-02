"""SQLite persistence layer.

Deliberately uses the stdlib sqlite3 module so there's no ORM magic to learn.
When you outgrow this (auth, relations, migrations), swap in SQLAlchemy.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "tickets.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
    requester_name     TEXT    NOT NULL,
    requester_email    TEXT    NOT NULL,
    subject            TEXT    NOT NULL,
    description        TEXT    NOT NULL,
    status             TEXT    NOT NULL DEFAULT 'open',
    category           TEXT    NOT NULL DEFAULT 'unclassified',
    priority           TEXT    NOT NULL DEFAULT 'P3',
    suggested_response TEXT,
    triage_reasoning   TEXT
);

CREATE TABLE IF NOT EXISTS agents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL
);
"""

VALID_STATUSES = {"open", "in_progress", "resolved"}


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as db:
        db.executescript(SCHEMA)


def insert_ticket(
    requester_name: str,
    requester_email: str,
    subject: str,
    description: str,
    category: str,
    priority: str,
    suggested_response: str | None,
    triage_reasoning: str | None,
) -> dict:
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO tickets
                (requester_name, requester_email, subject, description,
                 category, priority, suggested_response, triage_reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                requester_name,
                requester_email,
                subject,
                description,
                category,
                priority,
                suggested_response,
                triage_reasoning,
            ),
        )
        row = db.execute(
            "SELECT * FROM tickets WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return dict(row)


def list_tickets() -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM tickets ORDER BY id DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_ticket(ticket_id: int) -> dict | None:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        return dict(row) if row else None


def update_ticket_status(ticket_id: int, status: str) -> dict | None:
    with get_db() as db:
        db.execute(
            "UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id)
        )
        row = db.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        return dict(row) if row else None


def ticket_stats() -> dict:
    with get_db() as db:
        by_category = db.execute(
            "SELECT category, COUNT(*) AS count FROM tickets GROUP BY category"
        ).fetchall()
        by_priority = db.execute(
            "SELECT priority, COUNT(*) AS count FROM tickets GROUP BY priority"
        ).fetchall()
        by_status = db.execute(
            "SELECT status, COUNT(*) AS count FROM tickets GROUP BY status"
        ).fetchall()
        return {
            "by_category": {r["category"]: r["count"] for r in by_category},
            "by_priority": {r["priority"]: r["count"] for r in by_priority},
            "by_status": {r["status"]: r["count"] for r in by_status},
        }


def create_agent(username: str, password_hash: str) -> dict:
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO agents (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        row = db.execute(
            "SELECT * FROM agents WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        return dict(row)


def get_agent_by_username(username: str) -> dict | None:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM agents WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None
