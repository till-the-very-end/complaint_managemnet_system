"""Database layer (SQLite). All SQL lives here."""
import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS complaints (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id TEXT UNIQUE NOT NULL,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL,
    description  TEXT NOT NULL,
    priority     TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'Pending',
    assigned_to  TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
"""


class DatabaseError(Exception):
    """Raised when a database operation fails."""


def get_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    conn = None
    try:
        conn = get_connection(db_path)
        with conn:
            conn.executescript(SCHEMA)
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not initialise database: {exc}") from exc
    finally:
        if conn:
            conn.close()


def _run(db_path, fn, message):
    """Open a connection, run fn(conn) in a transaction, always close, wrap errors."""
    conn = None
    try:
        conn = get_connection(db_path)
        with conn:
            return fn(conn)
    except sqlite3.Error as exc:
        raise DatabaseError(f"{message}: {exc}") from exc
    finally:
        if conn:
            conn.close()


def insert_complaint(db_path, data):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def op(conn):
        # Temporary unique value, replaced by the real ID once the row number is known
        cur = conn.execute(
            "INSERT INTO complaints (complaint_id, name, category, description, "
            "priority, status, assigned_to, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("TMP-" + now + data["name"], data["name"], data["category"], data["description"],
             data["priority"], data["status"], data["assigned_to"], now, now),
        )
        row_id = cur.lastrowid
        complaint_id = f"CMP-{datetime.now().year}-{row_id:04d}"
        conn.execute("UPDATE complaints SET complaint_id = ? WHERE id = ?", (complaint_id, row_id))
        return complaint_id

    return _run(db_path, op, "Could not save complaint")


def list_complaints(db_path, status=None):
    def op(conn):
        if status:
            rows = conn.execute(
                "SELECT * FROM complaints WHERE status = ? ORDER BY id DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM complaints ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]

    return _run(db_path, op, "Could not read complaints")


def get_complaint(db_path, complaint_id):
    def op(conn):
        row = conn.execute(
            "SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,)
        ).fetchone()
        return dict(row) if row else None

    return _run(db_path, op, "Could not read complaint")


def update_status(db_path, complaint_id, status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def op(conn):
        cur = conn.execute(
            "UPDATE complaints SET status = ?, updated_at = ? WHERE complaint_id = ?",
            (status, now, complaint_id),
        )
        return cur.rowcount > 0

    return _run(db_path, op, "Could not update complaint")


def status_counts(db_path):
    def op(conn):
        counts = {"Pending": 0, "In Progress": 0, "Resolved": 0}
        for row in conn.execute("SELECT status, COUNT(*) AS c FROM complaints GROUP BY status"):
            counts[row["status"]] = row["c"]
        return counts

    return _run(db_path, op, "Could not read counts")
