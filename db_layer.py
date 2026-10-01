"""Shared SQLite helpers: indexes, user layer, preserve across rebuild."""
from __future__ import annotations

import sqlite3
from pathlib import Path

USER_TABLES = ("user_favorites", "user_progress", "builds", "map_markers", "audit_log")

USER_DDL = [
    """CREATE TABLE IF NOT EXISTS user_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        item_id TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(table_name, item_id)
    )""",
    """CREATE TABLE IF NOT EXISTS user_progress (
        id TEXT PRIMARY KEY,
        kind TEXT,
        status TEXT,
        note TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS builds (
        id TEXT PRIMARY KEY,
        name TEXT,
        payload TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS map_markers (
        id TEXT PRIMARY KEY,
        name TEXT,
        lat REAL,
        lng REAL,
        note TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT,
        detail TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""",
]

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_deviations_name ON deviations(name)",
    "CREATE INDEX IF NOT EXISTS idx_weapons_name ON weapons(name)",
    "CREATE INDEX IF NOT EXISTS idx_armor_name ON armor(name)",
    "CREATE INDEX IF NOT EXISTS idx_mods_name ON mods(name)",
    "CREATE INDEX IF NOT EXISTS idx_bosses_name ON bosses(name)",
    "CREATE INDEX IF NOT EXISTS idx_locations_name ON locations(name)",
    "CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name)",
    "CREATE INDEX IF NOT EXISTS idx_materials_name ON materials(name)",
    "CREATE INDEX IF NOT EXISTS idx_tech_name ON tech(name)",
]


def snapshot_user(db_path: Path) -> dict[str, list[tuple]]:
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(str(db_path))
    out: dict[str, list[tuple]] = {}
    try:
        names = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        for table in USER_TABLES:
            if table not in names:
                continue
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            cols = [d[1] for d in conn.execute(f"PRAGMA table_info({table})")]
            out[table] = [cols, rows]  # type: ignore[list-item]
    finally:
        conn.close()
    return out


def apply_layer(conn: sqlite3.Connection) -> None:
    for ddl in USER_DDL:
        conn.execute(ddl)
    existing = {
        r[0]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    for stmt in INDEXES:
        table = stmt.split(" ON ")[1].split("(")[0]
        if table in existing:
            conn.execute(stmt)
    conn.execute(
        "INSERT INTO audit_log(action, detail) VALUES ('schema', 'user layer + indexes applied')"
    )


def restore_user(conn: sqlite3.Connection, snap: dict) -> None:
    apply_layer(conn)
    for table, payload in snap.items():
        if not payload or len(payload) != 2:
            continue
        cols, rows = payload
        if not rows:
            continue
        placeholders = ",".join("?" * len(cols))
        col_sql = ",".join(cols)
        conn.executemany(
            f"INSERT OR REPLACE INTO {table} ({col_sql}) VALUES ({placeholders})",
            rows,
        )
