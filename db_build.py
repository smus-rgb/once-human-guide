#!/usr/bin/env python3
"""Build once_human.db from module JSON or database_full.json.

Adds indexes, a unified entity catalog, FTS5 search, and name-based links
(ingredients, drops, sources, locations). User-layer data is a separate file
and is never written or deleted here.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "once_human.db"
SCHEMA_VERSION = "5.5-links-indexes"

MODULES = {
    "deviations": "deviations.json",
    "weapons": "weapons.json",
    "armor": "armor.json",
    "mods": "mods.json",
    "bosses": "bosses.json",
    "locations": "map_locations.json",
    "recipes": "recipes.json",
    "materials": "materials.json",
    "scenarios": "scenarios.json",
    "quests": "quests.json",
    "events": "events.json",
    "creatures": "creatures.json",
    "npcs": "npcs.json",
    "plants": "plants.json",
    "fish": "fish.json",
    "animals": "animals.json",
    "flowers": "flowers.json",
}

SCHEMAS = {
    "deviations": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, utility TEXT, desc TEXT, mood TEXT, source TEXT, tags TEXT",
                   ["id", "name", "type", "rarity", "utility", "desc", "mood", "source", "tags"]),
    "weapons": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, desc TEXT, tags TEXT",
                ["id", "name", "type", "rarity", "style", "desc", "tags"]),
    "armor": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, pieces TEXT, desc TEXT, tags TEXT",
              ["id", "name", "type", "rarity", "style", "pieces", "desc", "tags"]),
    "mods": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, slot TEXT, desc TEXT, source TEXT, tags TEXT",
             ["id", "name", "type", "rarity", "slot", "desc", "source", "tags"]),
    "bosses": ("id TEXT PRIMARY KEY, name TEXT, region TEXT, location TEXT, desc TEXT, drops TEXT",
               ["id", "name", "region", "location", "desc", "drops"]),
    "locations": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, x REAL, y REAL, desc TEXT",
                  ["id", "name", "type", "region", "x", "y", "desc"]),
    "recipes": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, station TEXT, ingredients TEXT, effect TEXT, desc TEXT",
                ["id", "name", "type", "station", "ingredients", "effect", "desc"]),
    "materials": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT",
                  ["id", "name", "type", "desc"]),
    "scenarios": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, phase TEXT, desc TEXT, rewards TEXT, locations TEXT, tags TEXT",
                  ["id", "name", "type", "phase", "desc", "rewards", "locations", "tags"]),
    "quests": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, desc TEXT, rewards TEXT, tags TEXT",
               ["id", "name", "type", "region", "desc", "rewards", "tags"]),
    "events": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, status TEXT, desc TEXT, rewards TEXT, location TEXT, timer TEXT, tags TEXT",
               ["id", "name", "type", "status", "desc", "rewards", "location", "timer", "tags"]),
    "creatures": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, threat TEXT, desc TEXT, location TEXT, tags TEXT",
                  ["id", "name", "type", "threat", "desc", "location", "tags"]),
    "npcs": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, location TEXT, desc TEXT, tags TEXT",
             ["id", "name", "type", "location", "desc", "tags"]),
    "plants": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, uses TEXT, tags TEXT",
               ["id", "name", "type", "desc", "uses", "tags"]),
    "fish": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, location TEXT, tags TEXT",
             ["id", "name", "type", "desc", "location", "tags"]),
    "animals": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, drops TEXT, location TEXT, taming TEXT, tags TEXT",
                ["id", "name", "type", "desc", "drops", "location", "taming", "tags"]),
    "flowers": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, tags TEXT",
                ["id", "name", "type", "desc", "tags"]),
}

INDEXES = {
    "deviations": ("type", "rarity"),
    "weapons": ("type", "rarity"),
    "armor": ("type", "rarity"),
    "mods": ("type", "rarity", "slot"),
    "bosses": ("region",),
    "locations": ("type", "region"),
    "recipes": ("type", "station"),
    "scenarios": ("type", "phase"),
    "quests": ("type", "region"),
    "events": ("type", "status"),
    "creatures": ("type", "threat"),
    "npcs": ("type",),
}

LINK_FIELDS = {
    "recipes": (("ingredients", "ingredient"),),
    "bosses": (("drops", "drops"), ("location", "located_at")),
    "deviations": (("source", "source"),),
    "mods": (("source", "source"),),
    "animals": (("drops", "drops"), ("location", "located_at")),
    "quests": (("rewards", "rewards"),),
    "events": (("rewards", "rewards"), ("location", "located_at")),
    "scenarios": (("rewards", "rewards"), ("locations", "located_at")),
    "plants": (("uses", "used_in"),),
    "creatures": (("location", "located_at"),),
    "npcs": (("location", "located_at"),),
    "fish": (("location", "located_at"),),
}


def _load_modules() -> dict:
    data = {}
    for table, filename in MODULES.items():
        path = BASE / filename
        if not path.exists():
            data[table] = []
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        data[table] = raw if isinstance(raw, list) else raw.get(table, [])
    return data


def load_pack() -> dict:
    full = BASE / "database_full.json"
    if full.exists():
        data = json.loads(full.read_text(encoding="utf-8"))
        if isinstance(data, dict) and any(k in data for k in MODULES):
            return data
    data = _load_modules()
    ver_path = BASE / "version.json"
    version = "local"
    if ver_path.exists():
        version = json.loads(ver_path.read_text(encoding="utf-8")).get("data_version", version)
    data["version"] = version
    return data


def _blob(row: dict) -> str:
    parts = []
    for key, value in row.items():
        if value is None:
            continue
        if isinstance(value, (list, dict)):
            parts.append(json.dumps(value, ensure_ascii=False))
        else:
            parts.append(str(value))
    return " ".join(parts)


def _norm(name: str) -> str:
    return " ".join((name or "").lower().replace("-", " ").replace("'", "").split())


def _labels(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return _labels(parsed)
        return [part.strip() for part in value.replace("/", ",").split(",") if part.strip()]
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict):
                out.append(str(item.get("name") or item.get("id") or ""))
            else:
                out.append(str(item))
        return [x for x in out if x]
    if isinstance(value, dict):
        return [str(value.get("name") or "")]
    return [str(value)]


def _link(c, seen: set, src_table: str, src_id: str, dst_table: str, dst_id: str, relation: str) -> int:
    if not src_id or not dst_id or (src_table, src_id) == (dst_table, dst_id):
        return 0
    key = (src_table, src_id, dst_table, dst_id, relation)
    if key in seen:
        return 0
    seen.add(key)
    c.execute(
        "INSERT OR IGNORE INTO links VALUES (?,?,?,?,?,?)",
        (src_table, src_id, dst_table, dst_id, relation, 1.0),
    )
    return 1


def build(db_path: Path | None = None) -> dict:
    data = load_pack()
    path = db_path or DB_PATH
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL")
    ver = data.get("version", "unknown")
    now = datetime.now(timezone.utc).isoformat()
    c.execute(
        "CREATE TABLE data_versions (table_name TEXT PRIMARY KEY, version TEXT, updated_at TEXT)"
    )
    c.execute("INSERT INTO data_versions VALUES ('all', ?, ?)", (ver, now))
    c.execute(
        """CREATE TABLE entities (
            table_name TEXT NOT NULL,
            id TEXT NOT NULL,
            name TEXT,
            kind TEXT,
            rarity TEXT,
            region TEXT,
            blob TEXT,
            PRIMARY KEY (table_name, id)
        )"""
    )
    c.execute("CREATE INDEX idx_entities_name ON entities(name)")
    c.execute("CREATE INDEX idx_entities_kind ON entities(kind)")
    c.execute(
        """CREATE TABLE links (
            src_table TEXT, src_id TEXT, dst_table TEXT, dst_id TEXT,
            relation TEXT, score REAL,
            PRIMARY KEY (src_table, src_id, dst_table, dst_id, relation)
        )"""
    )
    c.execute("CREATE INDEX idx_links_dst ON links(dst_table, dst_id)")
    total = 0
    catalog = []
    for table, (schema, cols) in SCHEMAS.items():
        c.execute(f"CREATE TABLE {table} ({schema})")
        c.execute(f"CREATE INDEX idx_{table}_name ON {table}(name)")
        for col in INDEXES.get(table, ()):
            c.execute(f"CREATE INDEX idx_{table}_{col} ON {table}({col})")
        for row in data.get(table, []):
            vals = []
            for col in cols:
                value = row.get(col)
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                vals.append(value)
            c.execute(
                f"INSERT OR REPLACE INTO {table} VALUES ({','.join('?' * len(cols))})",
                vals,
            )
            catalog.append((table, row))
            total += 1
    by_name: dict[str, list[tuple[str, str]]] = {}
    for table, row in catalog:
        name = row.get("name") or ""
        c.execute(
            "INSERT OR REPLACE INTO entities VALUES (?,?,?,?,?,?,?)",
            (
                table,
                row.get("id"),
                name,
                row.get("type") or row.get("utility") or "",
                row.get("rarity") or "",
                row.get("region") or row.get("location") or "",
                _blob(row),
            ),
        )
        key = _norm(name)
        if len(key) >= 4:
            by_name.setdefault(key, []).append((table, row.get("id")))
    seen: set = set()
    link_count = 0
    for table, row in catalog:
        for field, relation in LINK_FIELDS.get(table, ()):
            text_bits = _labels(row.get(field))
            blob = " | ".join(text_bits).lower()
            if not blob:
                continue
            for key, hits in by_name.items():
                if key not in blob and key not in _norm(blob):
                    continue
                for dst_table, dst_id in hits:
                    link_count += _link(c, seen, table, row.get("id"), dst_table, dst_id, relation)
    c.execute(
        "CREATE VIRTUAL TABLE entities_fts USING fts5(table_name, id, name, blob, tokenize='unicode61')"
    )
    c.execute(
        "INSERT INTO entities_fts(table_name, id, name, blob) SELECT table_name, id, name, blob FROM entities"
    )
    c.execute(
        "INSERT INTO data_versions VALUES ('schema', ?, ?)",
        (SCHEMA_VERSION, now),
    )
    conn.commit()
    conn.close()
    return {
        "records": total,
        "links": link_count,
        "version": ver,
        "schema": SCHEMA_VERSION,
        "db": str(path),
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False))
