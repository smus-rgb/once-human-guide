"""Once Human Guide API — FastAPI + SQLite + FTS search + static shell."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "once_human.db"
if not DB_PATH.exists():
    DB_PATH = BASE.parent / "once_human.db"

DATA_VERSION = "2026-10-09-v19.2-372"
API_VERSION = "5.5.0"
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

if (BASE / "modules").is_dir():
    app.mount("/modules", StaticFiles(directory=BASE / "modules"), name="modules")


def get_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(503, f"Database not found at {DB_PATH}. Run python db_build.py")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_list(rows) -> list[dict]:
    items = [dict(r) for r in rows]
    for item in items:
        for key in ("tags", "ingredients", "drops", "locations", "pieces"):
            if key in item and isinstance(item[key], str):
                try:
                    item[key] = json.loads(item[key] or "[]")
                except Exception:
                    pass
    return items


FILTER_COLS = ("type", "rarity", "region", "slot", "status", "phase")
USER_DB = BASE / "once_human_user.db"


def user_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(USER_DB))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS favorites (
            id TEXT PRIMARY KEY,
            table_name TEXT NOT NULL,
            item_id TEXT NOT NULL,
            name TEXT,
            created_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def fetch_all(
    table: str,
    q: str | None = None,
    limit: int = 500,
    offset: int = 0,
    filters: dict | None = None,
) -> list[dict]:
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    where, params = [], []
    if q:
        where.append("(lower(name) LIKE ? OR lower(coalesce(desc,'')) LIKE ?)")
        params.extend([f"%{q.lower()}%", f"%{q.lower()}%"])
    for col, val in (filters or {}).items():
        if not val or col not in FILTER_COLS:
            continue
        where.append(f"lower(coalesce({col},'')) = ?")
        params.append(val.lower())
    sql = f"SELECT * FROM {table}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.Error as exc:
        conn.close()
        raise HTTPException(500, str(exc)) from exc
    conn.close()
    return rows_to_list(rows)


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
            "version": "/version",
            "stats": "/stats",
            "search": "/search?q=",
            "integrity": "/integrity",
            "links": "/links/{table}/{id}",
            "export": "/export",
            "maps": "/maps",
        },
    }


@app.get("/health")
def health():
    ok = DB_PATH.exists()
    return {"ok": ok, "db": str(DB_PATH), "api_version": API_VERSION}


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
    path = BASE / "ohg_data.js"
    if not path.exists():
        raise HTTPException(404, "ohg_data.js missing")
    return FileResponse(path, media_type="application/javascript")


@app.get("/ohg_sw.js")
def sw_js():
    path = BASE / "ohg_sw.js"
    if not path.exists():
        raise HTTPException(404, "ohg_sw.js missing")
    return FileResponse(path, media_type="application/javascript")


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
    }


@app.get("/maps")
def maps():
    return {"embeds": MAP_EMBEDS, "local_markers": True}


@app.get("/stats")
def stats():
    conn = get_db()
    out = {}
    total = 0
    for table in TABLES:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except Exception:
            n = 0
        out[table] = n
        total += n
    try:
        out["links"] = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        out["fts"] = conn.execute("SELECT COUNT(*) FROM entities_fts").fetchone()[0]
    except Exception:
        out["links"] = 0
        out["fts"] = 0
    conn.close()
    out["total"] = total
    out["data_version"] = DATA_VERSION
    return out


@app.get("/integrity")
def integrity():
    conn = get_db()
    issues = []
    counts = {}
    for table in TABLES:
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            empty = conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE name IS NULL OR trim(name)=''"
            ).fetchone()[0]
        except sqlite3.Error as exc:
            issues.append({"table": table, "error": str(exc)})
            continue
        counts[table] = n
        if empty:
            issues.append({"table": table, "empty_names": empty})
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    conn.close()
    return {
        "ok": quick == "ok" and not issues,
        "quick_check": quick,
        "counts": counts,
        "issues": issues,
        "expected_records": 372,
    }


def _fts_query(q: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in q)
    parts = [p for p in cleaned.split() if p]
    return " ".join(p + "*" for p in parts) or "ohg"


@app.get("/search")
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
    table: str | None = None,
):
    conn = get_db()
    try:
        match = _fts_query(q)
        sql = """SELECT table_name, id, name, blob
               FROM entities_fts
               WHERE entities_fts MATCH ?"""
        params: list = [match]
        if table and table in TABLES:
            sql += " AND table_name = ?"
            params.append(table)
        sql += " LIMIT ?"
        params.append(limit)
        rows = conn.execute(sql, params).fetchall()
        mode = "fts"
    except sqlite3.Error:
        rows = conn.execute(
            """SELECT table_name, id, name, blob FROM entities
               WHERE lower(name) LIKE ? OR lower(blob) LIKE ?
               LIMIT ?""",
            (f"%{q.lower()}%", f"%{q.lower()}%", limit),
        ).fetchall()
        mode = "like"
    conn.close()
    results = [
        {"table": r["table_name"], "id": r["id"], "name": r["name"], "snippet": (r["blob"] or "")[:180]}
        for r in rows
    ]
    return {"q": q, "mode": mode, "count": len(results), "results": results}


@app.get("/links/{table}/{item_id}")
def links(table: str, item_id: str):
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT l.dst_table, l.dst_id, l.relation, l.score, e.name
               FROM links l
               LEFT JOIN entities e ON e.table_name=l.dst_table AND e.id=l.dst_id
               WHERE l.src_table=? AND l.src_id=?
               UNION
               SELECT l.src_table, l.src_id, l.relation, l.score, e.name
               FROM links l
               LEFT JOIN entities e ON e.table_name=l.src_table AND e.id=l.src_id
               WHERE l.dst_table=? AND l.dst_id=?""",
            (table, item_id, table, item_id),
        ).fetchall()
    except sqlite3.Error:
        rows = []
    conn.close()
    return {"table": table, "id": item_id, "links": [dict(r) for r in rows]}


@app.get("/export")
def export_all():
    data = {"version": DATA_VERSION, "exported_at": datetime.now(timezone.utc).isoformat()}
    for table in TABLES:
        data[table] = fetch_all(table, limit=2000)
    return data


@app.get("/db-file")
def db_file():
    if not DB_PATH.exists():
        raise HTTPException(404, "SQLite file missing")
    return FileResponse(str(DB_PATH), filename="once_human.db")


def _list(table: str, q: str | None = None, limit: int = 500, offset: int = 0, **filters):
    return fetch_all(table, q, limit, offset, filters)


@app.get("/deviations")
def list_deviations(type: str | None = None, rarity: str | None = None, q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("deviations", q, limit, offset, type=type, rarity=rarity)


@app.get("/weapons")
def list_weapons(q: str | None = None, limit: int = 500, offset: int = 0, type: str | None = None, rarity: str | None = None):
    return _list("weapons", q, limit, offset, type=type, rarity=rarity)


@app.get("/armor")
def list_armor(q: str | None = None, limit: int = 500, offset: int = 0, type: str | None = None, rarity: str | None = None):
    return _list("armor", q, limit, offset, type=type, rarity=rarity)


@app.get("/mods")
def list_mods(q: str | None = None, limit: int = 500, offset: int = 0, type: str | None = None, rarity: str | None = None, slot: str | None = None):
    return _list("mods", q, limit, offset, type=type, rarity=rarity, slot=slot)


@app.get("/bosses")
def list_bosses(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("bosses", q, limit, offset)


@app.get("/locations")
def list_locations(q: str | None = None, limit: int = 500, offset: int = 0, type: str | None = None, region: str | None = None):
    return _list("locations", q, limit, offset, type=type, region=region)


@app.get("/recipes")
def list_recipes(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("recipes", q, limit, offset)


@app.get("/materials")
def list_materials(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("materials", q, limit, offset)


@app.get("/scenarios")
def list_scenarios(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("scenarios", q, limit, offset)


@app.get("/quests")
def list_quests(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("quests", q, limit, offset)


@app.get("/events")
def list_events(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("events", q, limit, offset)


@app.get("/creatures")
def list_creatures(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("creatures", q, limit, offset)


@app.get("/npcs")
def list_npcs(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("npcs", q, limit, offset)


@app.get("/plants")
def list_plants(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("plants", q, limit, offset)


@app.get("/fish")
def list_fish(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("fish", q, limit, offset)


@app.get("/animals")
def list_animals(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("animals", q, limit, offset)


@app.get("/flowers")
def list_flowers(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("flowers", q, limit, offset)



@app.get("/user/favorites")
def list_favorites():
    conn = user_db()
    rows = conn.execute("SELECT * FROM favorites ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/user/favorites")
def add_favorite(table: str, item_id: str, name: str | None = None):
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = user_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO favorites VALUES (?,?,?,?,?)",
        (f"{table}:{item_id}", table, item_id, name or item_id, now),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "id": f"{table}:{item_id}"}


@app.delete("/user/favorites/{table}/{item_id}")
def del_favorite(table: str, item_id: str):
    conn = user_db()
    conn.execute("DELETE FROM favorites WHERE id=?", (f"{table}:{item_id}",))
    conn.commit()
    conn.close()
    return {"ok": True}


@app.get("/update/check")
def update_check():
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
            headers={"User-Agent": "OnceHumanGuide-API/5.5"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            remote = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"ok": False, "error": str(exc), "local": local, "update_available": False}
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
            "released_at": remote.get("released_at"),
            "notes": remote.get("notes"),
        },
    }


@app.post("/update/run")
def update_run(force: bool = False):
    import subprocess
    import sys

    updater = BASE / "updater.py"
    if not updater.exists():
        raise HTTPException(404, "updater.py not found")
    cmd = [sys.executable, str(updater)]
    if force:
        cmd.append("--force")
    try:
        proc = subprocess.run(cmd, cwd=str(BASE), capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(504, "Update timed out") from exc
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
