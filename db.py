"""
db.py — SQLite data layer for the Hostel Management System.

Tables:
    users        -> login accounts (student / admin)
    rooms        -> hostel room inventory
    allocations  -> per-user "important details" tied to a room
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "hostel.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                role TEXT NOT NULL DEFAULT 'student',   -- 'student' or 'admin'
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_no TEXT UNIQUE NOT NULL,
                room_type TEXT NOT NULL,      -- Single / Double / Triple / Dorm
                floor INTEGER NOT NULL,
                capacity INTEGER NOT NULL,
                occupied INTEGER NOT NULL DEFAULT 0,
                fee_per_month REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                guardian_name TEXT,
                guardian_phone TEXT,
                emergency_contact TEXT,
                id_proof_type TEXT,
                id_proof_number TEXT,
                blood_group TEXT,
                address TEXT,
                check_in_date TEXT,
                status TEXT NOT NULL DEFAULT 'active',   -- 'active' or 'vacated'
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            );
            """
        )

        # Seed a default admin account and a few rooms on first run.
        cur = conn.execute("SELECT COUNT(*) AS c FROM users")
        if cur.fetchone()["c"] == 0:
            conn.execute(
                "INSERT INTO users (username, password_hash, full_name, role, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                ("admin", hash_password("admin123"), "Hostel Admin", "admin", now()),
            )

        cur = conn.execute("SELECT COUNT(*) AS c FROM rooms")
        if cur.fetchone()["c"] == 0:
            sample_rooms = [
                ("G-101", "Single", 1, 1, 3500.0),
                ("G-102", "Double", 1, 2, 2500.0),
                ("F1-201", "Double", 2, 2, 2500.0),
                ("F1-202", "Triple", 2, 3, 2000.0),
                ("F2-301", "Dorm", 3, 6, 1200.0),
            ]
            conn.executemany(
                "INSERT INTO rooms (room_no, room_type, floor, capacity, occupied, fee_per_month) "
                "VALUES (?, ?, ?, ?, 0, ?)",
                sample_rooms,
            )


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ---------- Users ----------

def create_user(username, password, full_name, email, phone, role="student"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, full_name, email, phone, role, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, hash_password(password), full_name, email, phone, role, now()),
        )


def authenticate(username, password):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, hash_password(password)),
        ).fetchone()
        return dict(row) if row else None


def username_exists(username):
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        return row is not None


def get_all_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
        return [dict(r) for r in rows]


# ---------- Rooms ----------

def get_all_rooms():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM rooms ORDER BY floor, room_no").fetchall()
        return [dict(r) for r in rows]


def get_available_rooms():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM rooms WHERE occupied < capacity ORDER BY floor, room_no"
        ).fetchall()
        return [dict(r) for r in rows]


def add_room(room_no, room_type, floor, capacity, fee_per_month):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO rooms (room_no, room_type, floor, capacity, occupied, fee_per_month) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (room_no, room_type, floor, capacity, fee_per_month),
        )


def _adjust_occupancy(conn, room_id, delta):
    conn.execute(
        "UPDATE rooms SET occupied = occupied + ? WHERE id = ?", (delta, room_id)
    )


# ---------- Allocations (the "important details" per user) ----------

def get_active_allocation(user_id):
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT a.*, r.room_no, r.room_type, r.floor, r.fee_per_month
            FROM allocations a
            JOIN rooms r ON a.room_id = r.id
            WHERE a.user_id = ? AND a.status = 'active'
            """,
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def create_allocation(user_id, room_id, details: dict):
    with get_conn() as conn:
        room = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
        if room is None:
            raise ValueError("Room not found.")
        if room["occupied"] >= room["capacity"]:
            raise ValueError("Room is already full.")

        conn.execute(
            """
            INSERT INTO allocations
                (user_id, room_id, guardian_name, guardian_phone, emergency_contact,
                 id_proof_type, id_proof_number, blood_group, address, check_in_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                user_id,
                room_id,
                details.get("guardian_name"),
                details.get("guardian_phone"),
                details.get("emergency_contact"),
                details.get("id_proof_type"),
                details.get("id_proof_number"),
                details.get("blood_group"),
                details.get("address"),
                details.get("check_in_date"),
            ),
        )
        _adjust_occupancy(conn, room_id, 1)


def vacate_allocation(allocation_id, room_id):
    with get_conn() as conn:
        conn.execute(
            "UPDATE allocations SET status = 'vacated' WHERE id = ?", (allocation_id,)
        )
        _adjust_occupancy(conn, room_id, -1)


def get_all_allocations():
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT a.*, u.username, u.full_name, r.room_no, r.room_type
            FROM allocations a
            JOIN users u ON a.user_id = u.id
            JOIN rooms r ON a.room_id = r.id
            WHERE a.status = 'active'
            ORDER BY r.room_no
            """
        ).fetchall()
        return [dict(r) for r in rows]
