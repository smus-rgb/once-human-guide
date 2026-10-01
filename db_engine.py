"""Shared SQLite rebuild for Once Human Guide.

Installer and updater both call rebuild_sqlite() so the schema stays one source of truth.
User-layer data (favorites, inventory, builds) is never stored here.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

TABLES = [
    "deviations", "weapons", "armor", "mods", "bosses", "locations",
    "recipes", "materials", "scenarios", "quests", "events", "creatures",
    "npcs", "plants", "fish", "animals", "flowers",
]

SCHEMAS: dict[str, tuple[str, list[str]]] = {
    "deviations": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, utility TEXT, desc TEXT, mood TEXT, source TEXT, tags TEXT",
        ["id", "name", "type", "rarity", "utility", "desc", "mood", "source", "tags"],
    ),
    "weapons": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, desc TEXT, tags TEXT",
        ["id", "name", "type", "rarity", "style", "desc", "tags"],
    ),
    "armor": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, desc TEXT, pieces INT, tags TEXT",
        ["id", "name", "type", "rarity", "style", "desc", "pieces", "tags"],
    ),
    "mods": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, slot TEXT, desc TEXT, tags TEXT",
        ["id", "name", "type", "rarity", "slot", "desc", "tags"],
    ),
    "bosses": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, location TEXT, desc TEXT, drops TEXT, tags TEXT",
        ["id", "name", "type", "region", "location", "desc", "drops", "tags"],
    ),
    "locations": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, desc TEXT, tags TEXT",
        ["id", "name", "type", "region", "desc", "tags"],
    ),
    "recipes": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, station TEXT, desc TEXT, ingredients TEXT, tags TEXT",
        ["id", "name", "type", "station", "desc", "ingredients", "tags"],
    ),
    "materials": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, desc TEXT, source TEXT, tags TEXT",
        ["id", "name", "type", "rarity", "desc", "source", "tags"],
    ),
    "scenarios": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, phase TEXT, desc TEXT, rewards TEXT, locations TEXT, tags TEXT",
        ["id", "name", "type", "phase", "desc", "rewards", "locations", "tags"],
    ),
    "quests": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, desc TEXT, rewards TEXT, tags TEXT",
        ["id", "name", "type", "region", "desc", "rewards", "tags"],
    ),
    "events": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, status TEXT, desc TEXT, rewards TEXT, location TEXT, timer TEXT, tags TEXT",
        ["id", "name", "type", "status", "desc", "rewards", "location", "timer", "tags"],
    ),
    "creatures": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, threat TEXT, desc TEXT, location TEXT, tags TEXT",
        ["id", "name", "type", "threat", "desc", "location", "tags"],
    ),
    "npcs": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, location TEXT, desc TEXT, tags TEXT",
        ["id", "name", "type", "location", "desc", "tags"],
    ),
    "plants": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, uses TEXT, tags TEXT",
        ["id", "name", "type", "desc", "uses", "tags"],
    ),
    "fish": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, location TEXT, tags TEXT",
        ["id", "name", "type", "desc", "location", "tags"],
    ),
    "animals": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, drops TEXT, location TEXT, taming TEXT, tags TEXT",
        ["id", "name", "type", "desc", "drops", "location", "taming", "tags"],
    ),
    "flowers": (
        "id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, tags TEXT",
        ["id", "name", "type", "desc", "tags"],
    ),
}


def pack_report(data: dict) -> dict:
    """Integrity report over the canonical JSON pack. Does not mutate user data."""
    missing_name = []
    missing_id = []
    seen: dict[str, str] = {}
    dups = []
    counts = {}
    for table in TABLES:
        rows = data.get(table) or []
        counts[table] = len(rows)
        for row in rows:
            rid = str(row.get("id") or "")
            if not rid:
                missing_id.append(table)
            elif rid in seen:
                dups.append({"id": rid, "tables": [seen[rid], table]})
            else:
                seen[rid] = table
            if not str(row.get("name") or "").strip():
                missing_name.append({"table": table, "id": rid})
    return {
        "ok": not missing_name and not missing_id and not dups,
        "records": sum(counts.values()),
        "counts": counts,
        "duplicate_ids": dups,
        "missing_name": missing_name,
        "missing_id": missing_id,
        "version": data.get("version"),
    }


def rebuild_sqlite(json_path: Path, db_path: Path) -> int:
    """Rebuild SQLite from database_full.json. Returns total row count."""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    c.execute(
        "CREATE TABLE data_versions (table_name TEXT PRIMARY KEY, version TEXT, updated_at TEXT)"
    )
    ver = data.get("version", "unknown")
    now = datetime.now(timezone.utc).isoformat()
    c.execute("INSERT INTO data_versions VALUES ('all', ?, ?)", (ver, now))
    report = pack_report(data)
    c.execute(
        "INSERT INTO data_versions VALUES ('integrity', ?, ?)",
        ("ok" if report["ok"] else "warn", now),
    )
    total = 0
    c.execute(
        """CREATE TABLE entity_index (
            table_name TEXT NOT NULL,
            id TEXT NOT NULL,
            name TEXT,
            type TEXT,
            region TEXT,
            search_text TEXT,
            payload TEXT,
            PRIMARY KEY (table_name, id)
        )"""
    )
    for table, (schema, cols) in SCHEMAS.items():
        c.execute(f"CREATE TABLE {table} ({schema})")
        for row in data.get(table, []):
            vals = []
            for col in cols:
                v = row.get(col)
                if isinstance(v, (list, dict)):
                    v = json.dumps(v, ensure_ascii=False)
                vals.append(v)
            c.execute(
                f"INSERT INTO {table} VALUES ({','.join('?' * len(cols))})",
                vals,
            )
            blob_parts = []
            for col in ("name", "type", "desc", "region", "location", "source", "utility", "rarity", "style", "slot", "tags"):
                v = row.get(col)
                if isinstance(v, list):
                    blob_parts.append(" ".join(str(x) for x in v))
                elif v:
                    blob_parts.append(str(v))
            c.execute(
                "INSERT INTO entity_index VALUES (?,?,?,?,?,?,?)",
                (
                    table,
                    str(row.get("id") or ""),
                    row.get("name"),
                    row.get("type"),
                    row.get("region") or row.get("location"),
                    " ".join(blob_parts).lower(),
                    json.dumps(row, ensure_ascii=False),
                ),
            )
            total += 1
        c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_name ON {table}(name)")
        if "type" in cols:
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_type ON {table}(type)")
        if "region" in cols:
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_region ON {table}(region)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entity_index(name)")
    c.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS entity_fts USING fts5(table_name, id, name, search_text, tokenize='unicode61')"
    )
    c.execute(
        "INSERT INTO entity_fts(table_name, id, name, search_text) SELECT table_name, id, name, search_text FROM entity_index"
    )
    conn.commit()
    conn.close()
    return total
