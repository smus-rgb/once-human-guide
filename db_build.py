#!/usr/bin/env python3
"""Build once_human.db from module JSON or database_full.json.

Adds indexes, a unified entity catalog, FTS5 search with diacritics removal, and name-based links.
User-layer data is never written here.
"""
from __future__ import annotations

import json
import re
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


def _release_meta() -> dict:
    """version.json is the single release source (pack version, patch target)."""
    path = BASE / "version.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_pack() -> dict:
    full = BASE / "database_full.json"
    if full.exists():
        data = json.loads(full.read_text(encoding="utf-8"))
        if isinstance(data, dict) and any(k in data for k in MODULES):
            # The pack JSON carries its own, older version string. version.json wins,
            # otherwise /version, /stats, the DB and the shell disagree (see AGENTS.md).
            data["version"] = _release_meta().get("data_version", data.get("version", "local"))
            return data
    data = _load_modules()
    data["version"] = _release_meta().get("data_version", "local")
    return data


def write_pack_js(data: dict) -> Path:
    """Regenerate ohg_data.js from the pack, so shell, DB and version.json agree."""
    meta = _release_meta()
    tables = {table: data.get(table, []) for table in MODULES if table in data}
    records = sum(len(rows) for rows in tables.values())
    payload = {
        "version": data.get("version", "local"),
        "patch": meta.get("patch_target", "") or "",
        "app": meta.get("app_version", "") or "",
        "shell": meta.get("shell_version", "") or "",
        "sw": meta.get("sw_cache", "") or "",
        "entities": records,
        "counts": {table: len(rows) for table, rows in tables.items()},
    }
    path = BASE / "ohg_data.js"
    path.write_text(
        "window.OHG_DATA=" + json.dumps(tables, ensure_ascii=False) + ";\n"
        + "window.OHG_META=" + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    return path


def stamp_release(version: str) -> list[str]:
    """Stamp the release version into the asset URLs and the service worker cache.

    Browsers keep unversioned scripts from their own cache for a long time
    (heuristic freshness is a share of the file's age), so a released module can
    stay invisible for hours. The shell, the service worker cache and
    version.json are stamped from the one version in version.json.
    """
    changed: list[str] = []
    shell = BASE / "once_human_guide_v19.html"
    if shell.exists():
        html = shell.read_text(encoding="utf-8")
        stamped = re.sub(
            r'(<script src="(?:ohg_data\.js|modules/[a-z_]+\.js))(?:\?v=[^"]*)?"',
            r'\1?v=' + version + '"',
            html,
        )
        if stamped != html:
            shell.write_text(stamped, encoding="utf-8")
            changed.append(shell.name)
    sw = BASE / "ohg_sw.js"
    if sw.exists():
        text = sw.read_text(encoding="utf-8")
        stamped = re.sub(r"const CACHE = '[^']*';", "const CACHE = 'ohg-" + version + "';", text, count=1)
        if stamped != text:
            sw.write_text(stamped, encoding="utf-8")
            changed.append(sw.name)
    meta_path = BASE / "version.json"
    if meta_path.exists():
        meta = meta_path.read_text(encoding="utf-8")
        stamped = re.sub(r'"sw_cache": "[^"]*"', '"sw_cache": "ohg-' + version + '"', meta, count=1)
        if stamped != meta:
            meta_path.write_text(stamped, encoding="utf-8")
            changed.append(meta_path.name)
    return changed


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


_LABEL_SPLIT = re.compile(r"\s*(?:/|,|;|&|\+|\||→|->)\s*")


def _label_keys(label: str) -> list[str]:
    """One field can carry several names ("Metal Scraps / Ingots", "Harveseed, Tar
    Pudding"); try the whole label and each part, so one label can resolve to more
    than one entity."""
    text = str(label or "").strip()
    keys: list[str] = []
    for candidate in [text] + _LABEL_SPLIT.split(text):
        key = _norm(candidate)
        if key and key not in keys:
            keys.append(key)
    return keys


def _add_links(c, src_table, src_id, labels, relation, by_name, link_count):
    for label in labels:
        if not label:
            continue
        for key in _label_keys(label):
            for dst_table, dst_id in by_name.get(key, []):
                if dst_table == src_table:
                    continue
                c.execute(
                    "INSERT OR IGNORE INTO links VALUES (?,?,?,?,?,?)",
                    (src_table, src_id, dst_table, dst_id, relation, 1.0),
                )
                link_count += 1
    return link_count


def _add_text_links(c, src_table, src_id, text, relation, by_name, link_count):
    """Link a prose field ("Silo Alpha secondary boss; Monolith of Thirst") by the
    entity names that actually occur in it. Only names of six characters or more,
    on word boundaries, so a short name ("Acid") cannot match inside another word
    ("Acidic"); the lower score marks such a link as derived from text."""
    haystack = _norm(text)
    if not haystack:
        return link_count
    for key, hits in by_name.items():
        if len(key) < 6:
            continue
        if not re.search(r"(?<![a-z0-9])" + re.escape(key) + r"(?![a-z0-9])", haystack):
            continue
        for dst_table, dst_id in hits:
            if dst_table == src_table:
                continue
            c.execute(
                "INSERT OR IGNORE INTO links VALUES (?,?,?,?,?,?)",
                (src_table, src_id, dst_table, dst_id, relation, 0.6),
            )
            link_count += 1
    return link_count


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
        if "type" in cols:
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_type ON {table}(type)")
        if "rarity" in cols:
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_rarity ON {table}(rarity)")
        if "region" in cols:
            c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_region ON {table}(region)")
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
        if key:
            by_name.setdefault(key, []).append((table, row.get("id")))
    link_count = 0
    # Recipes -> ingredients
    for row in data.get("recipes", []):
        ingredients = row.get("ingredients") or []
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                ingredients = []
        labels = [ing.get("name") if isinstance(ing, dict) else str(ing) for ing in ingredients]
        link_count = _add_links(c, "recipes", row.get("id"), labels, "ingredient", by_name, link_count)
    # Bosses -> drops
    for row in data.get("bosses", []):
        drops = row.get("drops") or []
        if isinstance(drops, str):
            try:
                drops = json.loads(drops)
            except json.JSONDecodeError:
                drops = [drops] if drops else []
        labels = [d.get("name") if isinstance(d, dict) else str(d) for d in drops]
        link_count = _add_links(c, "bosses", row.get("id"), labels, "drop", by_name, link_count)
        # location
        loc = row.get("location")
        if loc:
            link_count = _add_links(c, "bosses", row.get("id"), [loc], "located_at", by_name, link_count)
    # Animals -> drops
    for row in data.get("animals", []):
        drops = row.get("drops") or []
        if isinstance(drops, str):
            try:
                drops = json.loads(drops)
            except json.JSONDecodeError:
                drops = [drops] if drops else []
        labels = [d.get("name") if isinstance(d, dict) else str(d) for d in drops]
        link_count = _add_links(c, "animals", row.get("id"), labels, "drop", by_name, link_count)
    # Quests/events/scenarios -> rewards / locations
    for tbl, rel in (("quests", "reward"), ("events", "reward"), ("scenarios", "reward")):
        for row in data.get(tbl, []):
            rewards = row.get("rewards") or []
            if isinstance(rewards, str):
                try:
                    rewards = json.loads(rewards)
                except json.JSONDecodeError:
                    rewards = [rewards] if rewards else []
            labels = [r.get("name") if isinstance(r, dict) else str(r) for r in rewards]
            link_count = _add_links(c, tbl, row.get("id"), labels, rel, by_name, link_count)
            loc = row.get("location") or row.get("locations")
            if loc:
                locs = loc if isinstance(loc, list) else [loc]
                link_count = _add_links(c, tbl, row.get("id"), locs, "located_at", by_name, link_count)
    # Further fields that name other entities (locations, quests, drops, uses)
    field_links = (
        ("creatures", "location", "located_at"),
        ("creatures", "drops", "drop"),
        ("animals", "location", "located_at"),
        ("plants", "location", "located_at"),
        ("plants", "uses", "used_for"),
        ("fish", "location", "located_at"),
        ("npcs", "location", "located_at"),
        ("npcs", "quests", "gives_quest"),
    )
    for table, field, relation in field_links:
        for row in data.get(table, []):
            value = row.get(field)
            if not value:
                continue
            values = value if isinstance(value, list) else [value]
            labels = [v.get("name") if isinstance(v, dict) else str(v) for v in values]
            link_count = _add_links(c, table, row.get("id"), labels, relation, by_name, link_count)
    # Prose fields that mention locations and bosses by name
    for table in ("deviations", "mods", "materials", "creatures"):
        for row in data.get(table, []):
            link_count = _add_text_links(
                c, table, row.get("id"), row.get("source") or row.get("weaknesses"),
                "source", by_name, link_count,
            )
    c.execute(
        "CREATE VIRTUAL TABLE entities_fts USING fts5(table_name, id, name, blob, tokenize='unicode61 remove_diacritics 2')"
    )
    c.execute(
        "INSERT INTO entities_fts(table_name, id, name, blob) SELECT table_name, id, name, blob FROM entities"
    )
    c.execute(
        """CREATE TABLE data_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            severity TEXT NOT NULL,
            code TEXT NOT NULL,
            table_name TEXT,
            entity_id TEXT,
            detail TEXT
        )"""
    )
    c.execute("CREATE INDEX idx_issues_code ON data_issues(code)")
    c.execute("CREATE INDEX idx_links_src ON links(src_table, src_id)")
    c.execute("CREATE INDEX idx_links_dst ON links(dst_table, dst_id)")
    issue_count = 0

    def issue(severity, code, table, entity_id, detail):
        nonlocal issue_count
        c.execute(
            "INSERT INTO data_issues (severity, code, table_name, entity_id, detail) VALUES (?,?,?,?,?)",
            (severity, code, table, entity_id, detail),
        )
        issue_count += 1

    seen = {}
    for table, row in catalog:
        eid = row.get("id")
        name = (row.get("name") or "").strip()
        if not eid:
            issue("error", "missing_id", table, None, name or "(bez jména)")
        else:
            key = (table, str(eid))
            if key in seen:
                issue("error", "duplicate_id", table, str(eid), name)
            seen[key] = name
        if not name:
            issue("warn", "empty_name", table, eid, "prázdné name")
    for row in data.get("recipes", []):
        ingredients = row.get("ingredients") or []
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except json.JSONDecodeError:
                ingredients = []
        for ing in ingredients:
            label = ing.get("name") if isinstance(ing, dict) else str(ing)
            if not any(by_name.get(key) for key in _label_keys(label)):
                issue("info", "unresolved_ingredient", "recipes", row.get("id"), label)
    c.execute(
        "INSERT INTO data_versions VALUES ('schema', '5.5-audit-links-diacritics-expanded', ?)",
        (now,),
    )
    conn.commit()
    conn.close()
    pack_js = None
    stamped: list[str] = []
    if db_path is None:
        # Refreshing the repo DB also refreshes the shell pack and the cache keys,
        # so the version sources cannot drift apart and a release reaches browsers.
        pack_js = write_pack_js(data)
        stamped = stamp_release(str(ver))
    return {
        "records": total,
        "links": link_count,
        "issues": issue_count,
        "version": ver,
        "db": str(path),
        "pack_js": str(pack_js) if pack_js else None,
        "stamped": stamped,
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False))
