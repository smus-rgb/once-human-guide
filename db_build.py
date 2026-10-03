#!/usr/bin/env python3
"""Build once_human.db from module JSON or database_full.json.

Adds indexes, a unified entity catalog, FTS5 search, and name-based links.
User-layer data is never written here.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "once_human.db"

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

# Known columns stay queryable. Anything else lands in extra so pack fields are not dropped.
SCHEMAS = {
    "deviations": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, utility TEXT, desc TEXT, mood TEXT, source TEXT, tags TEXT, extra TEXT",
                   ["id", "name", "type", "rarity", "utility", "desc", "mood", "source", "tags"]),
    "weapons": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, desc TEXT, tags TEXT, extra TEXT",
                ["id", "name", "type", "rarity", "style", "desc", "tags"]),
    "armor": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, pieces TEXT, desc TEXT, tags TEXT, extra TEXT",
              ["id", "name", "type", "rarity", "style", "pieces", "desc", "tags"]),
    "mods": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, slot TEXT, desc TEXT, source TEXT, tags TEXT, extra TEXT",
             ["id", "name", "type", "rarity", "slot", "desc", "source", "tags"]),
    "bosses": ("id TEXT PRIMARY KEY, name TEXT, region TEXT, location TEXT, desc TEXT, drops TEXT, extra TEXT",
               ["id", "name", "region", "location", "desc", "drops"]),
    "locations": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, x REAL, y REAL, desc TEXT, extra TEXT",
                  ["id", "name", "type", "region", "x", "y", "desc"]),
    "recipes": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, station TEXT, ingredients TEXT, effect TEXT, desc TEXT, extra TEXT",
                ["id", "name", "type", "station", "ingredients", "effect", "desc"]),
    "materials": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, extra TEXT",
                  ["id", "name", "type", "desc"]),
    "scenarios": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, phase TEXT, desc TEXT, rewards TEXT, locations TEXT, tags TEXT, extra TEXT",
                  ["id", "name", "type", "phase", "desc", "rewards", "locations", "tags"]),
    "quests": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, location TEXT, desc TEXT, objectives TEXT, rewards TEXT, prereq TEXT, tags TEXT, extra TEXT",
               ["id", "name", "type", "region", "location", "desc", "objectives", "rewards", "prereq", "tags"]),
    "events": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, status TEXT, desc TEXT, rewards TEXT, location TEXT, timer TEXT, tags TEXT, extra TEXT",
               ["id", "name", "type", "status", "desc", "rewards", "location", "timer", "tags"]),
    "creatures": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, threat TEXT, level TEXT, desc TEXT, weaknesses TEXT, drops TEXT, location TEXT, tags TEXT, extra TEXT",
                  ["id", "name", "type", "threat", "level", "desc", "weaknesses", "drops", "location", "tags"]),
    "npcs": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, location TEXT, desc TEXT, services TEXT, quests TEXT, tags TEXT, extra TEXT",
             ["id", "name", "type", "location", "desc", "services", "quests", "tags"]),
    "plants": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, desc TEXT, uses TEXT, location TEXT, respawn TEXT, tags TEXT, extra TEXT",
               ["id", "name", "type", "rarity", "desc", "uses", "location", "respawn", "tags"]),
    "fish": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, bait TEXT, location TEXT, conditions TEXT, rewards TEXT, tags TEXT, extra TEXT",
             ["id", "name", "type", "desc", "bait", "location", "conditions", "rewards", "tags"]),
    "animals": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, drops TEXT, location TEXT, taming TEXT, tags TEXT, extra TEXT",
                ["id", "name", "type", "desc", "drops", "location", "taming", "tags"]),
    "flowers": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, desc TEXT, genetics TEXT, mutations TEXT, result TEXT, tags TEXT, extra TEXT",
                ["id", "name", "type", "desc", "genetics", "mutations", "result", "tags"]),
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
    return " ".join((name or "").lower().replace("-", " ").split())


def build(db_path: Path | None = None) -> dict:
    data = load_pack()
    path = db_path or DB_PATH
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode=WAL")
    ver = data.get("version", "unknown")
    ver_path = BASE / "version.json"
    if ver_path.exists():
        ver = json.loads(ver_path.read_text(encoding="utf-8")).get("data_version", ver)
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
    c.execute(
        """CREATE TABLE links (
            src_table TEXT, src_id TEXT, dst_table TEXT, dst_id TEXT,
            relation TEXT, score REAL,
            PRIMARY KEY (src_table, src_id, dst_table, dst_id, relation)
        )"""
    )
    total = 0
    catalog = []
    for table, (schema, cols) in SCHEMAS.items():
        c.execute(f"CREATE TABLE {table} ({schema})")
        c.execute(f"CREATE INDEX idx_{table}_name ON {table}(name)")
        for row in data.get(table, []):
            vals = []
            for col in cols:
                value = row.get(col)
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                vals.append(value)
            extra = {k: v for k, v in row.items() if k not in cols and k not in ("id",)}
            vals.append(json.dumps(extra, ensure_ascii=False) if extra else None)
            c.execute(
                f"INSERT OR REPLACE INTO {table} VALUES ({','.join('?' * len(vals))})",
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
        if key:
            by_name.setdefault(key, []).append((table, row.get("id")))
    link_count = 0
    for row in data.get("recipes", []):
        ingredients = row.get("ingredients") or []
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                ingredients = []
        for ing in ingredients:
            label = ing.get("name") if isinstance(ing, dict) else str(ing)
            hit = by_name.get(_norm(label))
            if not hit:
                continue
            for dst_table, dst_id in hit:
                if dst_table == "recipes":
                    continue
                c.execute(
                    "INSERT OR IGNORE INTO links VALUES (?,?,?,?,?,?)",
                    ("recipes", row.get("id"), dst_table, dst_id, "ingredient", 1.0),
                )
                link_count += 1
    loc_by_name = {}
    for row in data.get("locations", []):
        key = _norm(row.get("name") or "")
        if key:
            loc_by_name.setdefault(key, ("locations", row.get("id")))
    for table in ("bosses", "creatures", "quests", "npcs", "events", "plants", "fish", "animals"):
        for row in data.get(table, []):
            label = row.get("location") or row.get("region") or ""
            hit = loc_by_name.get(_norm(str(label)))
            if not hit:
                continue
            c.execute(
                "INSERT OR IGNORE INTO links VALUES (?,?,?,?,?,?)",
                (table, row.get("id"), hit[0], hit[1], "located_at", 0.8),
            )
            link_count += 1
    c.execute(
        "CREATE VIRTUAL TABLE entities_fts USING fts5(table_name, id, name, blob, tokenize='unicode61')"
    )
    c.execute(
        "INSERT INTO entities_fts(table_name, id, name, blob) SELECT table_name, id, name, blob FROM entities"
    )
    c.execute(
        "INSERT INTO data_versions VALUES ('schema', '5.5-preserve-links', ?)",
        (now,),
    )
    conn.commit()
    conn.close()
    return {"records": total, "links": link_count, "version": ver, "db": str(path)}


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False))
