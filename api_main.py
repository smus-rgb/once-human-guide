"""Once Human Guide API — FastAPI + SQLite + search + export"""
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

DATA_VERSION = "2026-09-30-v18-372"
API_VERSION = "5.2.0"
MAP_EMBEDS = {
    "thgl": "https://oncehuman.th.gl",
    "mapgenie": "https://mapgenie.io/once-human/maps/nalcott",
}

TABLES = [
    "deviations", "weapons", "armor", "mods", "bosses", "locations",
    "recipes", "materials", "scenarios", "quests", "events", "creatures",
    "npcs", "plants", "fish", "animals", "flowers",
]

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
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(500, str(e))
    conn.close()
    items = rows_to_list(rows)
    if q:
        s = q.lower()
        def match(item: dict) -> bool:
            blob = " ".join(
                str(item.get(k) or "")
                for k in ("name", "desc", "type", "region", "location", "source", "utility", "rarity", "style")
            ).lower()
            tags = item.get("tags") or []
            return s in blob or any(s in str(t).lower() for t in tags)
        items = [i for i in items if match(i)]
    return items


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
            "version": "/version",
            "stats": "/stats",
            "search": "/search?q=",
            "export": "/export",
            "maps": "/maps",
            "table": "/{table}",
            "item": "/{table}/{id}",
        },
    }


@app.get("/ui")
def serve_ui():
    html = BASE / "once_human_guide_ui_v4.html"
    if not html.exists():
        html = BASE / "once_human_guide_app.html"
    if not html.exists():
        raise HTTPException(404, "UI HTML not found")
    return HTMLResponse(html.read_text(encoding="utf-8"))


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
    conn.close()
    out["total"] = total
    out["data_version"] = DATA_VERSION
    return out


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=200)):
    s = q.lower()
    results = []
    for table in TABLES:
        for item in fetch_all(table):
            blob = " ".join(str(v) for v in item.values() if v is not None).lower()
            if s in blob:
                results.append({"table": table, **item})
            if len(results) >= limit:
                return {"q": q, "count": len(results), "results": results}
    return {"q": q, "count": len(results), "results": results}


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


# Generic table routes
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
            headers={"User-Agent": "OnceHumanGuide-API/5.0"},
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
            "data_version": remote.get("data_version"),
            "released_at": remote.get("released_at"),
            "notes": remote.get("notes"),
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
