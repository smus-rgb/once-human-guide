"""Once Human Guide API — FastAPI + SQLite + FTS search + static shell."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "once_human.db"
if not DB_PATH.exists():
    DB_PATH = BASE.parent / "once_human.db"

DATA_VERSION = "2026-10-01-v19-372"
API_VERSION = "5.4.0"
MAP_EMBEDS = {
    "thgl": "https://oncehuman.th.gl",
    "mapgenie": "https://mapgenie.io/once-human/maps/nalcott",
}

TABLES = [
    "deviations", "weapons", "armor", "mods", "bosses", "locations",
    "recipes", "materials", "scenarios", "quests", "events", "creatures",
    "npcs", "plants", "fish", "animals", "flowers",
]
MODULE_FILES = {
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

app = FastAPI(
    title="Once Human Guide API",
    version=API_VERSION,
    description="Game companion data API for Once Human Guide",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(503, f"Database not found at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_list(rows) -> list[dict]:
    items = [dict(r) for r in rows]
    for i in items:
        for key in ("tags", "ingredients"):
            if key in i and isinstance(i[key], str):
                try:
                    i[key] = json.loads(i[key] or "[]")
                except Exception:
                    i[key] = []
    return items


def fetch_all(table: str, q: str | None = None) -> list[dict]:
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    try:
        if q:
            rows = conn.execute(
                f"SELECT * FROM {table} WHERE lower(coalesce(name,'')) LIKE ? OR lower(coalesce(desc,'')) LIKE ?",
                (f"%{q.lower()}%", f"%{q.lower()}%"),
            ).fetchall()
        else:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(500, str(e))
    conn.close()
    return rows_to_list(rows)


def _json_counts() -> dict[str, int]:
    out = {}
    for table, fname in MODULE_FILES.items():
        fp = BASE / fname
        if not fp.exists():
            out[table] = -1
            continue
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            out[table] = len(data) if isinstance(data, list) else -1
        except Exception:
            out[table] = -1
    return out


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": "Once Human Guide API",
        "api_version": API_VERSION,
        "data_version": DATA_VERSION,
        "tables": TABLES,
        "endpoints": {
            "ui": "/ui",
            "health": "/health",
            "integrity": "/integrity",
            "version": "/version",
            "stats": "/stats",
            "search": "/search?q=",
            "export": "/export",
            "maps": "/maps",
            "table": "/{table}",
            "item": "/{table}/{id}",
        },
    }


@app.get("/health")
def health():
    db_ok = DB_PATH.exists()
    ui_ok = (BASE / "once_human_guide_v19.html").exists()
    modules_ok = all((BASE / "modules" / n).exists() for n in (
        "ohg_runtime.js", "ohg_map.js", "ohg_builds.js", "ohg_pack_channel.js",
    ))
    return {
        "ok": db_ok and ui_ok and modules_ok,
        "api_version": API_VERSION,
        "db": str(DB_PATH) if db_ok else None,
        "ui": ui_ok,
        "modules": modules_ok,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ui")
def serve_ui():
    for name in (
        "once_human_guide_v19.html",
        "once_human_guide_v18.html",
        "once_human_guide_ui_v4.html",
        "once_human_guide_app.html",
    ):
        html = BASE / name
        if html.exists():
            return HTMLResponse(html.read_text(encoding="utf-8"))
    raise HTTPException(404, "UI HTML not found")


@app.get("/ohg_data.js")
def pack_js():
    fp = BASE / "ohg_data.js"
    if not fp.exists():
        raise HTTPException(404, "ohg_data.js missing")
    return FileResponse(str(fp), media_type="application/javascript")


@app.get("/ohg_sw.js")
def sw_js():
    fp = BASE / "ohg_sw.js"
    if not fp.exists():
        raise HTTPException(404, "ohg_sw.js missing")
    return FileResponse(str(fp), media_type="application/javascript")


@app.get("/modules/{name}")
def module_js(name: str):
    if "/" in name or ".." in name or not name.endswith(".js"):
        raise HTTPException(404, "module not found")
    fp = BASE / "modules" / name
    if not fp.exists():
        raise HTTPException(404, "module not found")
    return FileResponse(str(fp), media_type="application/javascript")


@app.get("/version")
def version():
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT version, updated_at FROM data_versions WHERE table_name='all'"
        ).fetchone()
        ver = row["version"] if row else DATA_VERSION
        updated = row["updated_at"] if row else None
    except Exception:
        ver, updated = DATA_VERSION, None
    finally:
        conn.close()
    return {
        "data_version": ver,
        "api_version": API_VERSION,
        "updated_at": updated,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "maps": MAP_EMBEDS,
        "record_hint": "GET /stats",
    }


@app.get("/maps")
def maps():
    return {"embeds": MAP_EMBEDS, "local_markers": True}


@app.get("/stats")
def stats():
    conn = get_db()
    c = conn.cursor()
    out = {}
    total = 0
    for t in TABLES:
        try:
            n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception:
            n = 0
        out[t] = n
        total += n
    fts = False
    try:
        conn.execute("SELECT 1 FROM search_fts LIMIT 1")
        fts = True
    except Exception:
        fts = False
    conn.close()
    out["total"] = total
    out["data_version"] = DATA_VERSION
    out["fts"] = fts
    return out


@app.get("/integrity")
def integrity():
    """Compare module JSON counts with SQLite. Pack stays canonical."""
    json_counts = _json_counts()
    sqlite_counts = {}
    issues = []
    fts = False
    if not DB_PATH.exists():
        return {"ok": False, "error": "sqlite missing", "json": json_counts}
    conn = get_db()
    try:
        for t in TABLES:
            try:
                n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception as e:
                n = -1
                issues.append(f"{t}: {e}")
            sqlite_counts[t] = n
            jn = json_counts.get(t, -1)
            if jn >= 0 and n >= 0 and jn != n:
                issues.append(f"{t}: json {jn} != sqlite {n}")
            if n >= 0:
                dup = conn.execute(
                    f"SELECT id, COUNT(*) c FROM {t} GROUP BY id HAVING c > 1"
                ).fetchall()
                for row in dup:
                    issues.append(f"{t}: duplicate id {row['id']}")
                missing = conn.execute(
                    f"SELECT COUNT(*) FROM {t} WHERE id IS NULL OR trim(id)='' OR name IS NULL OR trim(name)=''"
                ).fetchone()[0]
                if missing:
                    issues.append(f"{t}: {missing} rows missing id or name")
        try:
            conn.execute("SELECT 1 FROM search_fts LIMIT 1")
            fts = True
        except Exception:
            issues.append("search_fts missing — rebuild DB via updater.py")
    finally:
        conn.close()
    jtot = sum(v for v in json_counts.values() if v >= 0)
    stot = sum(v for v in sqlite_counts.values() if v >= 0)
    return {
        "ok": not issues,
        "match": jtot == stot and not issues,
        "json_total": jtot,
        "sqlite_total": stot,
        "expected_records": 372,
        "fts": fts,
        "json": json_counts,
        "sqlite": sqlite_counts,
        "issues": issues,
    }


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=200)):
    conn = get_db()
    results = []
    try:
        try:
            rows = conn.execute(
                "SELECT table_name, item_id, name, snippet(search_fts, 3, '', '', '…', 12) AS snippet "
                "FROM search_fts WHERE search_fts MATCH ? LIMIT ?",
                (q.replace('"', "") + "*", limit),
            ).fetchall()
            for row in rows:
                results.append({
                    "table": row["table_name"],
                    "id": row["item_id"],
                    "name": row["name"],
                    "snippet": row["snippet"],
                })
            if results:
                return {"q": q, "count": len(results), "engine": "fts5", "results": results}
        except sqlite3.Error:
            pass
        like = f"%{q.lower()}%"
        for table in TABLES:
            rows = conn.execute(
                f"SELECT * FROM {table} WHERE lower(coalesce(name,'')) LIKE ? OR lower(coalesce(desc,'')) LIKE ? LIMIT ?",
                (like, like, limit - len(results)),
            ).fetchall()
            for row in rows:
                results.append({"table": table, **rows_to_list([row])[0]})
                if len(results) >= limit:
                    return {"q": q, "count": len(results), "engine": "like", "results": results}
    finally:
        conn.close()
    return {"q": q, "count": len(results), "engine": "like", "results": results}


@app.get("/export")
def export_all():
    data = {"version": DATA_VERSION, "exported_at": datetime.now(timezone.utc).isoformat()}
    for t in TABLES:
        data[t] = fetch_all(t)
    return data


@app.get("/db-file")
def db_file():
    if not DB_PATH.exists():
        raise HTTPException(404, "SQLite file missing")
    return FileResponse(str(DB_PATH), filename="once_human.db")


@app.get("/deviations")
def list_deviations(type: str | None = None, q: str | None = None):
    items = fetch_all("deviations", q)
    if type:
        items = [i for i in items if (i.get("type") or "").lower() == type.lower()]
    return items


@app.get("/weapons")
def list_weapons(q: str | None = None):
    return fetch_all("weapons", q)


@app.get("/armor")
def list_armor(q: str | None = None):
    return fetch_all("armor", q)


@app.get("/mods")
def list_mods(q: str | None = None):
    return fetch_all("mods", q)


@app.get("/bosses")
def list_bosses(q: str | None = None):
    return fetch_all("bosses", q)


@app.get("/locations")
def list_locations(q: str | None = None):
    return fetch_all("locations", q)


@app.get("/recipes")
def list_recipes(q: str | None = None):
    return fetch_all("recipes", q)


@app.get("/materials")
def list_materials(q: str | None = None):
    return fetch_all("materials", q)


@app.get("/scenarios")
def list_scenarios(q: str | None = None):
    return fetch_all("scenarios", q)


@app.get("/quests")
def list_quests(q: str | None = None):
    return fetch_all("quests", q)


@app.get("/events")
def list_events(q: str | None = None):
    return fetch_all("events", q)


@app.get("/creatures")
def list_creatures(q: str | None = None):
    return fetch_all("creatures", q)


@app.get("/npcs")
def list_npcs(q: str | None = None):
    return fetch_all("npcs", q)


@app.get("/plants")
def list_plants(q: str | None = None):
    return fetch_all("plants", q)


@app.get("/fish")
def list_fish(q: str | None = None):
    return fetch_all("fish", q)


@app.get("/animals")
def list_animals(q: str | None = None):
    return fetch_all("animals", q)


@app.get("/flowers")
def list_flowers(q: str | None = None):
    return fetch_all("flowers", q)


@app.get("/update/check")
def update_check():
    """Compare local version.json with GitHub remote."""
    import urllib.request

    local_path = BASE / "version.json"
    local = {}
    if local_path.exists():
        local = json.loads(local_path.read_text(encoding="utf-8"))
    raw = (local.get("github") or {}).get("raw_base") or (
        "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main"
    )
    try:
        req = urllib.request.Request(
            f"{raw}/version.json",
            headers={"User-Agent": "OnceHumanGuide-API/5.4"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            remote = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "local": local,
            "update_available": False,
        }
    available = (remote.get("data_version") != local.get("data_version")) or (
        remote.get("app_version") != local.get("app_version")
    )
    return {
        "ok": True,
        "update_available": available,
        "local": {
            "app_version": local.get("app_version"),
            "data_version": local.get("data_version"),
        },
        "remote": {
            "app_version": remote.get("app_version"),
            "shell_version": remote.get("shell_version"),
            "data_version": remote.get("data_version"),
            "records": remote.get("records"),
            "sw_cache": remote.get("sw_cache"),
            "released_at": remote.get("released_at"),
            "notes": remote.get("notes"),
        },
        "shell": {
            "ui": "/ui",
            "host": "once_human_guide_v19.html",
            "fallback": "once_human_guide_v18.html",
            "modules": [
                "modules/ohg_runtime.js",
                "modules/ohg_map.js",
                "modules/ohg_builds.js",
                "modules/ohg_pack_channel.js",
            ],
        },
    }


@app.post("/update/run")
def update_run(force: bool = False):
    """Run updater.py in-process (downloads from GitHub, rebuilds SQLite)."""
    import subprocess
    import sys

    updater = BASE / "updater.py"
    if not updater.exists():
        raise HTTPException(404, "updater.py not found")
    cmd = [sys.executable, str(updater)]
    if force:
        cmd.append("--force")
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(BASE),
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Update timed out")
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:] if proc.stdout else "",
        "stderr": proc.stderr[-2000:] if proc.stderr else "",
    }


@app.get("/{table}/{item_id}")
def get_item(table: str, item_id: str):
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, f"{table}/{item_id} not found")
    return rows_to_list([row])[0]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=False)
