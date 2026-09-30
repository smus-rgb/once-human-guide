"""Once Human Guide API – FastAPI + SQLite + online version/search"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "once_human.db"
if not DB_PATH.exists():
    DB_PATH = Path(__file__).resolve().parent.parent / "once_human.db"

DATA_VERSION = "2026-09-30-v3"
MAP_EMBEDS = {
    "thgl": "https://oncehuman.th.gl",
    "mapgenie": "https://mapgenie.io/once-human/maps/nalcott",
}

app = FastAPI(title="Once Human Guide API", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_db():
    if not DB_PATH.exists():
        raise HTTPException(503, "Database not found")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_list(rows, tag_key="tags"):
    items = [dict(r) for r in rows]
    for i in items:
        if tag_key in i and isinstance(i[tag_key], str):
            try:
                i[tag_key] = json.loads(i[tag_key] or "[]")
            except Exception:
                i[tag_key] = []
        if "ingredients" in i and isinstance(i["ingredients"], str):
            try:
                i["ingredients"] = json.loads(i["ingredients"] or "[]")
            except Exception:
                i["ingredients"] = []
    return items


@app.get("/")
def root():
    return {
        "status": "ok",
        "app": "Once Human Guide API",
        "version": "3.0.0",
        "data_version": DATA_VERSION,
        "endpoints": ["/version", "/stats", "/deviations", "/weapons", "/armor", "/mods",
                      "/bosses", "/locations", "/recipes", "/search?q=", "/export", "/maps"],
    }


@app.get("/version")
def version():
    conn = get_db()
    try:
        row = conn.execute("SELECT version, updated_at FROM data_versions WHERE table_name='all'").fetchone()
        ver = row["version"] if row else DATA_VERSION
        updated = row["updated_at"] if row else None
    except Exception:
        ver, updated = DATA_VERSION, None
    finally:
        conn.close()
    return {
        "data_version": ver,
        "api_version": "3.0.0",
        "updated_at": updated,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "maps": MAP_EMBEDS,
        "download_hint": "GET /export for full JSON snapshot",
    }


@app.get("/maps")
def maps():
    return {"embeds": MAP_EMBEDS, "local_markers": True}


@app.get("/stats")
def stats():
    conn = get_db()
    c = conn.cursor()
    out = {}
    for t in ["deviations", "weapons", "armor", "mods", "bosses", "locations", "recipes", "materials"]:
        try:
            out[t] = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        except Exception:
            out[t] = 0
    conn.close()
    out["data_version"] = DATA_VERSION
    return out


@app.get("/deviations")
def list_deviations(type: str | None = None, q: str | None = None):
    conn = get_db()
    rows = conn.execute("SELECT * FROM deviations").fetchall()
    conn.close()
    items = rows_to_list(rows)
    if type:
        items = [i for i in items if (i.get("type") or "").lower() == type.lower()]
    if q:
        s = q.lower()
        items = [i for i in items if s in (i.get("name") or "").lower() or s in (i.get("desc") or "").lower()
                 or any(s in t for t in (i.get("tags") or [])) or s in (i.get("source") or "").lower()]
    return items


@app.get("/weapons")
def list_weapons(q: str | None = None):
    conn = get_db()
    rows = conn.execute("SELECT * FROM weapons").fetchall()
    conn.close()
    items = rows_to_list(rows)
    if q:
        s = q.lower()
        items = [i for i in items if s in (i.get("name") or "").lower() or s in (i.get("desc") or "").lower()]
    return items


@app.get("/armor")
def list_armor(q: str | None = None):
    conn = get_db()
    rows = conn.execute("SELECT * FROM armor").fetchall()
    conn.close()
    items = rows_to_list(rows)
    if q:
        s = q.lower()
        items = [i for i in items if s in (i.get("name") or "").lower() or s in (i.get("desc") or "").lower()]
    return items


@app.get("/mods")
def list_mods(q: str | None = None):
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM mods").fetchall()
    except Exception:
        conn.close()
        return []
    conn.close()
    items = rows_to_list(rows)
    if q:
        s = q.lower()
        items = [i for i in items if s in (i.get("name") or "").lower() or s in (i.get("desc") or "").lower()]
    return items


@app.get("/bosses")
def list_bosses():
    conn = get_db()
    rows = conn.execute("SELECT * FROM bosses").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/locations")
def list_locations():
    conn = get_db()
    rows = conn.execute("SELECT * FROM locations").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/recipes")
def list_recipes():
    conn = get_db()
    rows = conn.execute("SELECT * FROM recipes").fetchall()
    conn.close()
    return rows_to_list(rows, tag_key="ingredients")


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(50, ge=1, le=100)):
    results = []
    results.extend([{**d, "category": "deviation"} for d in list_deviations(q=q)])
    results.extend([{**w, "category": "weapon"} for w in list_weapons(q=q)])
    results.extend([{**a, "category": "armor"} for a in list_armor(q=q)])
    results.extend([{**m, "category": "mod"} for m in list_mods(q=q)])
    s = q.lower()
    for loc in list_locations():
        if s in (loc.get("name") or "").lower() or s in (loc.get("desc") or "").lower() or s in (loc.get("region") or "").lower():
            results.append({**loc, "category": "location"})
    for b in list_bosses():
        if s in (b.get("name") or "").lower() or s in (b.get("drops") or "").lower():
            results.append({**b, "category": "boss"})
    for r in list_recipes():
        if s in (r.get("name") or "").lower() or s in (r.get("desc") or "").lower():
            results.append({**r, "category": "recipe"})
    return results[:limit]


@app.get("/export")
def export_all():
    return {
        "version": DATA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "deviations": list_deviations(),
        "weapons": list_weapons(),
        "armor": list_armor(),
        "mods": list_mods(),
        "bosses": list_bosses(),
        "locations": list_locations(),
        "recipes": list_recipes(),
        "maps": MAP_EMBEDS,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
