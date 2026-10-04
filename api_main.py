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

def _meta() -> dict:
    path = BASE / "version.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

_META = _meta()
DATA_VERSION = _META.get("data_version", "2026-10-01-v19.1-372")
API_VERSION = _META.get("app_version", "5.5.0")
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


def fetch_all(table: str, q: str | None = None, limit: int = 500, offset: int = 0) -> list[dict]:
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    try:
        if q:
            rows = conn.execute(
                f"SELECT * FROM {table} WHERE lower(name) LIKE ? OR lower(coalesce(desc,'')) LIKE ? LIMIT ? OFFSET ?",
                (f"%{q.lower()}%", f"%{q.lower()}%", limit, offset),
            ).fetchall()
        else:
            rows = conn.execute(
                f"SELECT * FROM {table} LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
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
    if not DB_PATH.exists():
        return {"ok": False, "db": str(DB_PATH), "api_version": API_VERSION, "reason": "missing"}
    conn = sqlite3.connect(str(DB_PATH))
    try:
        quick = conn.execute("PRAGMA quick_check").fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        schema = conn.execute(
            "SELECT version FROM data_versions WHERE table_name='schema'"
        ).fetchone()
    except sqlite3.Error as exc:
        conn.close()
        return {"ok": False, "db": str(DB_PATH), "error": str(exc)}
    conn.close()
    return {
        "ok": quick == "ok" and total > 0,
        "db": str(DB_PATH),
        "api_version": API_VERSION,
        "records": total,
        "schema": schema[0] if schema else None,
        "quick_check": quick,
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
            dups = conn.execute(
                f"SELECT id, COUNT(*) c FROM {table} GROUP BY id HAVING c > 1"
            ).fetchall()
        except sqlite3.Error as exc:
            issues.append({"table": table, "error": str(exc)})
            continue
        counts[table] = n
        if empty:
            issues.append({"table": table, "empty_names": empty})
        for row in dups:
            issues.append({"table": table, "duplicate_id": row["id"], "count": row["c"]})
    try:
        stored = conn.execute(
            "SELECT kind, table_name, id, detail FROM data_issues LIMIT 50"
        ).fetchall()
        for row in stored:
            issues.append(dict(row))
    except sqlite3.Error:
        stored = []
    quick = conn.execute("PRAGMA quick_check").fetchone()[0]
    conn.close()
    total = sum(counts.values())
    return {
        "ok": quick == "ok" and not issues and total == 372,
        "quick_check": quick,
        "counts": counts,
        "issues": issues,
        "expected_records": 372,
        "records": total,
    }


def _fold(value: str) -> str:
    table = str.maketrans("áčďéěíňóřšťúůýžäöü", "acdeeinorstuuyzaou")
    return " ".join((value or "").lower().replace("-", " ").split()).translate(table)


@app.get("/search")
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
    table: str | None = None,
):
    if table and table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    folded = _fold(q)
    mode = "fts"
    try:
        match = q.replace('"', " ") + "*"
        sql = """SELECT table_name, id, name, blob FROM entities_fts WHERE entities_fts MATCH ?"""
        args: list = [match]
        if table:
            sql += " AND table_name = ?"
            args.append(table)
        sql += " LIMIT ?"
        args.append(limit)
        rows = conn.execute(sql, args).fetchall()
    except sqlite3.Error:
        rows = []
        mode = "like"
    if not rows:
        mode = "alias" if mode != "like" else mode
        try:
            sql = """SELECT e.table_name, e.id, e.name, e.blob
                     FROM aliases a JOIN entities e ON e.table_name=a.table_name AND e.id=a.id
                     WHERE a.alias LIKE ?"""
            args = [f"%{folded}%"]
            if table:
                sql += " AND a.table_name = ?"
                args.append(table)
            sql += " LIMIT ?"
            args.append(limit)
            rows = conn.execute(sql, args).fetchall()
            if rows:
                mode = "alias"
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


@app.get("/facets")
def facets():
    conn = get_db()
    out = {}
    for table in ("deviations", "weapons", "armor", "mods"):
        try:
            rows = conn.execute(
                f"SELECT coalesce(rarity,'(none)') AS rarity, COUNT(*) AS n FROM {table} GROUP BY rarity ORDER BY n DESC"
            ).fetchall()
            out[table] = [dict(r) for r in rows]
        except sqlite3.Error:
            out[table] = []
    conn.close()
    return out


@app.get("/links/{table}/{item_id}")
def links(table: str, item_id: str):
    if table not in TABLES:
        raise HTTPException(404, f"Unknown table: {table}")
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT dst_table, dst_id, relation, score FROM links
               WHERE src_table=? AND src_id=?
               UNION
               SELECT src_table, src_id, relation, score FROM links
               WHERE dst_table=? AND dst_id=?""",
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


def _list(table: str, q: str | None = None, limit: int = 500, offset: int = 0):
    return fetch_all(table, q, limit, offset)


@app.get("/deviations")
def list_deviations(type: str | None = None, q: str | None = None, limit: int = 500, offset: int = 0):
    items = _list("deviations", q, limit, offset)
    if type:
        items = [i for i in items if (i.get("type") or "").lower() == type.lower()]
    return items


@app.get("/weapons")
def list_weapons(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("weapons", q, limit, offset)


@app.get("/armor")
def list_armor(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("armor", q, limit, offset)


@app.get("/mods")
def list_mods(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("mods", q, limit, offset)


@app.get("/bosses")
def list_bosses(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("bosses", q, limit, offset)


@app.get("/locations")
def list_locations(q: str | None = None, limit: int = 500, offset: int = 0):
    return _list("locations", q, limit, offset)


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
