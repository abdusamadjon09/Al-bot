import sqlite3
from datetime import datetime

DB = "ai_video_bot.db"


def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                kind TEXT,
                status TEXT,
                details TEXT,
                created_at TEXT
            )
        """)


def save_user(user_id, username, first_name):
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            INSERT INTO users
            (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name
        """, (
            user_id,
            username,
            first_name,
            datetime.utcnow().isoformat()
        ))


def add_job(user_id, kind, status, details=""):
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            INSERT INTO jobs
            (user_id, kind, status, details, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            kind,
            status,
            details,
            datetime.utcnow().isoformat()
        ))


def list_jobs(user_id):
    with sqlite3.connect(DB) as conn:
        return conn.execute("""
            SELECT id, kind, status
            FROM jobs
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT 10
        """, (user_id,)).fetchall()


def stats():
    with sqlite3.connect(DB) as conn:
        users = conn.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        jobs = conn.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]

        return users, jobs
