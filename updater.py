#!/usr/bin/env python3
"""Once Human Guide — auto-updater

Checks GitHub for a newer version.json and downloads updated data/UI/API files.
Rebuilds once_human.db from database_full.json after data update.

Usage:
  python updater.py              # check + update if newer
  python updater.py --check      # only report remote vs local
  python updater.py --force      # always re-download
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOCAL_VERSION = BASE / "version.json"
DEFAULT_RAW = "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main"

# files the updater is allowed to replace
UPDATE_MAP = {
    "database_full.json": "database_full.json",
    "once_human_guide_v19.html": "once_human_guide_v19.html",
    "once_human_guide_v18.html": "once_human_guide_v18.html",
    "ohg_data.js": "ohg_data.js",
    "ohg_sw.js": "ohg_sw.js",
    "modules/ohg_runtime.js": "modules/ohg_runtime.js",
    "modules/ohg_map.js": "modules/ohg_map.js",
    "modules/ohg_builds.js": "modules/ohg_builds.js",
    "modules/ohg_pack_channel.js": "modules/ohg_pack_channel.js",
    "once_human_guide_ui_v4.html": "once_human_guide_ui_v4.html",
    "once_human_guide_app.html": "once_human_guide_app.html",
    "CHANGELOG.md": "CHANGELOG.md",
    "Once_Human_Guide_v18_Modular_System.md": "Once_Human_Guide_v18_Modular_System.md",
    "api_main.py": "api_main.py",
    "requirements.txt": "requirements.txt",
    "updater.py": "updater.py",
    "install.py": "install.py",
    "version.json": "version.json",
    "start.sh": "start.sh",
    "deviations.json": "deviations.json",
    "weapons.json": "weapons.json",
    "armor.json": "armor.json",
    "mods.json": "mods.json",
    "bosses.json": "bosses.json",
    "map_locations.json": "map_locations.json",
    "recipes.json": "recipes.json",
    "materials.json": "materials.json",
    "scenarios.json": "scenarios.json",
    "quests.json": "quests.json",
    "events.json": "events.json",
    "creatures.json": "creatures.json",
    "npcs.json": "npcs.json",
    "plants.json": "plants.json",
    "fish.json": "fish.json",
    "animals.json": "animals.json",
    "flowers.json": "flowers.json",
}


def load_local() -> dict:
    if LOCAL_VERSION.exists():
        return json.loads(LOCAL_VERSION.read_text(encoding="utf-8"))
    return {"app_version": "0.0.0", "data_version": "none"}


def fetch_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "OnceHumanGuide-Updater/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "OnceHumanGuide-Updater/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def ver_tuple(v: str) -> tuple:
    """Compare app semver-ish or data version strings."""
    # data versions like 2026-09-30-v5-complete sort lexicographically OK
    parts = []
    for p in v.replace("-", ".").split("."):
        if p.isdigit():
            parts.append((0, int(p)))
        else:
            parts.append((1, p))
    return tuple(parts)


def is_newer(remote: dict, local: dict) -> bool:
    try:
        if ver_tuple(remote.get("app_version", "0")) > ver_tuple(local.get("app_version", "0")):
            return True
    except Exception:
        pass
    return (remote.get("data_version") or "") != (local.get("data_version") or "")



MODULE_FILES = [
    ("deviations", "deviations.json"),
    ("weapons", "weapons.json"),
    ("armor", "armor.json"),
    ("mods", "mods.json"),
    ("bosses", "bosses.json"),
    ("locations", "map_locations.json"),
    ("recipes", "recipes.json"),
    ("materials", "materials.json"),
    ("scenarios", "scenarios.json"),
    ("quests", "quests.json"),
    ("events", "events.json"),
    ("creatures", "creatures.json"),
    ("npcs", "npcs.json"),
    ("plants", "plants.json"),
    ("fish", "fish.json"),
    ("animals", "animals.json"),
    ("flowers", "flowers.json"),
]


def assemble_database_full(base: Path) -> Path | None:
    """Build database_full.json from module JSON files if missing or empty."""
    full = base / "database_full.json"
    modules = {}
    for key, fname in MODULE_FILES:
        fp = base / fname
        if fp.exists():
            try:
                modules[key] = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                pass
    if not modules:
        return full if full.exists() else None
    ver = "assembled"
    vp = base / "version.json"
    if vp.exists():
        try:
            ver = json.loads(vp.read_text(encoding="utf-8")).get("data_version", ver)
        except Exception:
            pass
    data = {"version": ver, **modules}
    full.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[updater] assembled database_full.json from {len(modules)} modules")
    return full


def rebuild_sqlite(json_path: Path, db_path: Path) -> int:
    """Rebuild SQLite from database_full.json. Returns total row count."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    schemas = {
        "deviations": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, utility TEXT, desc TEXT, mood TEXT, source TEXT, tags TEXT",
                       ["id", "name", "type", "rarity", "utility", "desc", "mood", "source", "tags"]),
        "weapons": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, desc TEXT, tags TEXT",
                    ["id", "name", "type", "rarity", "style", "desc", "tags"]),
        "armor": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, style TEXT, desc TEXT, pieces INT, tags TEXT",
                  ["id", "name", "type", "rarity", "style", "desc", "pieces", "tags"]),
        "mods": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, slot TEXT, desc TEXT, tags TEXT",
                 ["id", "name", "type", "rarity", "slot", "desc", "tags"]),
        "bosses": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, location TEXT, desc TEXT, drops TEXT, tags TEXT",
                   ["id", "name", "type", "region", "location", "desc", "drops", "tags"]),
        "locations": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, region TEXT, desc TEXT, x REAL, y REAL, tags TEXT, extra TEXT",
                      ["id", "name", "type", "region", "desc", "x", "y", "tags", "extra"]),
        "recipes": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, station TEXT, desc TEXT, ingredients TEXT, effect TEXT, tags TEXT, extra TEXT",
                    ["id", "name", "type", "station", "desc", "ingredients", "effect", "tags", "extra"]),
        "materials": ("id TEXT PRIMARY KEY, name TEXT, type TEXT, rarity TEXT, desc TEXT, source TEXT, tags TEXT",
                      ["id", "name", "type", "rarity", "desc", "source", "tags"]),
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
    c.execute("CREATE TABLE data_versions (table_name TEXT PRIMARY KEY, version TEXT, updated_at TEXT)")
    ver = data.get("version", "unknown")
    c.execute("INSERT INTO data_versions VALUES ('all', ?, datetime('now'))", (ver,))
    total = 0
    index_cols = ("name", "type", "region", "rarity", "location")
    for table, (schema, cols) in schemas.items():
        if "extra TEXT" not in schema:
            schema = schema + ", extra TEXT"
            cols = cols + ["extra"]
        c.execute(f"CREATE TABLE {table} ({schema})")
        for col in index_cols:
            if col in cols:
                c.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{col} ON {table}({col})")
        for row in data.get(table, []):
            vals = []
            known = set(cols) - {"extra"}
            extra = {k: v for k, v in row.items() if k not in known}
            for col in cols:
                if col == "extra":
                    v = json.dumps(extra, ensure_ascii=False) if extra else None
                else:
                    v = row.get(col)
                if isinstance(v, (list, dict)):
                    v = json.dumps(v, ensure_ascii=False)
                vals.append(v)
            c.execute(f"INSERT INTO {table} VALUES ({','.join('?' * len(cols))})", vals)
            total += 1
    # FTS across name/desc for fast search
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(table_name UNINDEXED, id UNINDEXED, name, body)")
    for table in schemas:
        rows = c.execute(f"SELECT id, name, desc FROM {table}").fetchall()
        c.executemany(
            "INSERT INTO search_fts(table_name, id, name, body) VALUES (?,?,?,?)",
            [(table, r[0], r[1] or "", r[2] or "") for r in rows],
        )
    conn.commit()
    conn.close()
    return total


def run(check_only: bool = False, force: bool = False) -> int:
    local = load_local()
    raw_base = (local.get("github") or {}).get("raw_base") or DEFAULT_RAW
    remote_url = f"{raw_base}/version.json"
    print(f"[updater] local  app={local.get('app_version')} data={local.get('data_version')}")
    print(f"[updater] check  {remote_url}")
    try:
        remote = fetch_json(remote_url)
    except urllib.error.URLError as e:
        print(f"[updater] offline / network error: {e}")
        return 2
    except Exception as e:
        print(f"[updater] failed to read remote version: {e}")
        return 2

    print(f"[updater] remote app={remote.get('app_version')} data={remote.get('data_version')}")
    if not force and not is_newer(remote, local):
        print("[updater] already up to date")
        return 0
    if check_only:
        print("[updater] update available (check-only, no download)")
        return 1

    files = list(UPDATE_MAP.keys())
    # prefer remote files list if present
    remote_files = remote.get("files") or {}
    if remote_files:
        files = list(dict.fromkeys(list(remote_files.keys()) + files))

    updated = []
    for name in files:
        if name not in UPDATE_MAP:
            continue
        url = f"{raw_base}/{name}"
        dest = BASE / UPDATE_MAP[name]
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = fetch_bytes(url)
            dest.write_bytes(data)
            updated.append(name)
            print(f"[updater] downloaded {name} ({len(data)} bytes)")
        except Exception as e:
            print(f"[updater] skip {name}: {e}")

    # rebuild sqlite if database_full present
    full = BASE / "database_full.json"
    if not full.exists() or full.stat().st_size < 100:
        assemble_database_full(BASE)
        full = BASE / "database_full.json"
    if full.exists():
        n = rebuild_sqlite(full, BASE / "once_human.db")
        print(f"[updater] rebuilt once_human.db ({n} rows)")

    print(f"[updater] done — {len(updated)} files updated")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Once Human Guide auto-updater")
    ap.add_argument("--check", action="store_true", help="Only check for updates")
    ap.add_argument("--force", action="store_true", help="Force re-download")
    args = ap.parse_args()
    sys.exit(run(check_only=args.check, force=args.force))


if __name__ == "__main__":
    main()
