"""Guide content source — local guide.json with an optional Google Drive overlay.

Entity data stays canonical in the pack (JSON moduly / ohg_data.js / SQLite);
this module only serves the player guide text, so editing the guide never
touches the pack.

Environment (delivered by the platform, never hardcoded here):
  GOOGLE_API_KEY        API key with the Google Drive API enabled
  GOOGLE_DRIVE_FILE_ID  id of a Google Doc (exported as plain text) or of a
                        JSON file with the same shape as guide.json
  GUIDE_DRIVE_TTL       optional cache TTL in seconds (default 300)

The Drive file must be shared as "Anyone with the link", otherwise an API key
cannot read it. Without both variables the module serves the local guide.json.

Plain-text convention for a Google Doc:

  # Cesta: Nováček (0–2 h)
  > keywords: nováček, start

  ## Krok: Vyber scénář a založ postavu
  Cíl: Rozjet hru ve scénáři, který odpovídá tomu, co chceš hrát.
  Proč: Scénář určuje mapu i pravidla světa.
  Čas: 10 min
  Klíčová slova: scénář, manibus
  Odkazy: scenarios/sc_manibus, quests/q_tutorial
  - vyber scénář
  - dokonči úvodní quest
  ! Nováček začíná na Manibusu.

Headings `# FAQ` and `# Slovníček` switch the section: `## Otázka` (with the
following paragraph as answer) and `## Pojem` (with definition) are parsed into
`faq` and `glossary`.
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
GUIDE_PATH = BASE / "guide.json"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"
DEFAULT_TTL = 300

_cache: dict = {"at": 0.0, "doc": None, "error": None}


def api_key() -> str:
    return os.environ.get("GOOGLE_API_KEY", "").strip()


def file_id() -> str:
    return os.environ.get("GOOGLE_DRIVE_FILE_ID", "").strip()


def configured() -> bool:
    return bool(api_key() and file_id())


def load_local() -> dict | None:
    if not GUIDE_PATH.exists():
        return None
    try:
        return json.loads(GUIDE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _ttl() -> int:
    try:
        return max(0, int(os.environ.get("GUIDE_DRIVE_TTL", DEFAULT_TTL)))
    except ValueError:
        return DEFAULT_TTL


def _http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "OnceHumanGuide-Guide/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_drive_text() -> str:
    """Google Doc → plain text; ordinary file (e.g. JSON) → raw content."""
    key = urllib.parse.quote(api_key(), safe="")
    fid = urllib.parse.quote(file_id(), safe="")
    export = f"{DRIVE_API}/{fid}/export?mimeType=text/plain&key={key}"
    try:
        return _http_get(export)
    except Exception:
        return _http_get(f"{DRIVE_API}/{fid}?alt=media&key={key}")


def _steps_from_lines(lines: list[str], section: str):
    """Build one section (path / faq / glossary) from the document lines."""
    title = None
    items: list[dict] = []
    current: dict | None = None

    def close():
        nonlocal current
        if current and (current.get("title") or current.get("q") or current.get("term")):
            items.append(current)
        current = None

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue
        if stripped.startswith("## "):
            close()
            label = stripped[3:].strip()
            if section == "faq":
                current = {"id": f"faq-{len(items) + 1:02d}", "q": label, "a": "", "keywords": []}
            elif section == "glossary":
                current = {"term": label, "definition": "", "keywords": []}
            else:
                current = {"id": f"drive-{len(items) + 1:02d}", "title": label, "actions": [], "tips": [], "links": [], "keywords": []}
            continue
        if not stripped:
            continue
        if current is None:
            continue
        if stripped.startswith("> "):
            stripped = stripped[2:].strip()
        if stripped.startswith("- "):
            current.setdefault("actions", []).append(stripped[2:].strip())
            continue
        if stripped.startswith("! "):
            current.setdefault("tips", []).append(stripped[2:].strip())
            continue
        for key, field in (("Cíl:", "goal"), ("Proč:", "why"), ("Čas:", "time_estimate")):
            if stripped.lower().startswith(key.lower()):
                current[field] = stripped[len(key):].strip()
                break
        else:
            low = stripped.lower()
            if low.startswith("klíčová slova:"):
                current["keywords"] = [w.strip() for w in stripped.split(":", 1)[1].split(",") if w.strip()]
            elif low.startswith("odkazy:"):
                links = []
                for part in stripped.split(":", 1)[1].split(","):
                    chunk = part.strip()
                    if "/" in chunk:
                        table, _, ident = chunk.partition("/")
                        links.append({"table": table.strip(), "id": ident.strip(), "label": ident.strip()})
                current["links"] = links
            elif section == "faq":
                current["a"] = (current.get("a", "") + " " + stripped).strip()
            elif section == "glossary":
                current["definition"] = (current.get("definition", "") + " " + stripped).strip()
            else:
                current.setdefault("actions", []).append(stripped)
    close()
    return title, items


def parse_drive_text(text: str) -> dict:
    """Parse the plain-text convention into the guide.json shape."""
    sections: list[tuple[str, list[str]]] = []
    current_title = None
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            if current_title is not None or current_lines:
                sections.append((current_title or "", current_lines))
            current_title = line[2:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title is not None or current_lines:
        sections.append((current_title or "", current_lines))

    paths, faq, glossary = [], [], []
    for title, lines in sections:
        head = title.lower()
        if head.startswith("faq"):
            _, items = _steps_from_lines(lines, "faq")
            faq.extend(items)
        elif "slovní" in head or head.startswith("glossary"):
            _, items = _steps_from_lines(lines, "glossary")
            glossary.extend(items)
        else:
            path_title, items = _steps_from_lines(lines, "path")
            clean = title
            for prefix in ("cesta:", "path:"):
                if clean.lower().startswith(prefix):
                    clean = clean[len(prefix):].strip()
            paths.append({
                "id": clean.lower().replace(" ", "-") or f"path-{len(paths) + 1}",
                "title": clean or path_title or "Cesta",
                "summary": "",
                "phase": clean.lower().split(" ")[0] if clean else "",
                "keywords": [],
                "steps": items,
            })
    for path in paths:
        for step in path["steps"]:
            step.setdefault("source_refs", ["Google Drive"])
            step["verified_at"] = time.strftime("%Y-%m-%d")
    return {"paths": paths, "faq": faq, "glossary": glossary}


def effective(force: bool = False) -> dict | None:
    """Effective guide document: Drive overlay when configured, else local file."""
    local = load_local()
    if not configured():
        if local is None:
            return None
        local.setdefault("meta", {})["source"] = "local"
        local["meta"]["drive_configured"] = False
        return local

    fresh = _cache["doc"] is not None and (time.time() - _cache["at"]) < _ttl()
    if fresh and not force:
        return _cache["doc"]

    try:
        parsed = parse_drive_text(fetch_drive_text())
        meta = dict(local.get("meta", {}) if local else {})
        meta.update({
            "source": "drive",
            "drive_configured": True,
            "drive_file_id": file_id(),
            "synced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
        doc = {"meta": meta, "paths": parsed["paths"], "faq": parsed["faq"], "glossary": parsed["glossary"]}
        if not doc["paths"] and local:
            doc["paths"] = local.get("paths", [])
        _cache.update({"at": time.time(), "doc": doc, "error": None})
        return doc
    except Exception as exc:  # offline / wrong id / not shared → local guide
        _cache.update({"at": time.time(), "doc": None, "error": str(exc)})
        if local is None:
            return None
        local.setdefault("meta", {})["source"] = "local"
        local["meta"]["drive_configured"] = True
        local["meta"]["drive_error"] = str(exc)
        return local


def reload() -> dict:
    """Force a Drive refresh (used by POST /guide/reload)."""
    doc = effective(force=True)
    return {
        "ok": doc is not None and (doc.get("meta", {}).get("source") == "drive"),
        "configured": configured(),
        "source": (doc or {}).get("meta", {}).get("source"),
        "error": _cache.get("error"),
        "steps": sum(len(p.get("steps", [])) for p in (doc or {}).get("paths", [])),
    }
