#!/usr/bin/env python3
"""Once Human Guide — automatic installer (bootstrap)

One command installs everything from GitHub:
  downloads app + data, pip deps, SQLite, start scripts.

Usage:
  python3 install.py
  python3 install.py --dir ~/once-human-guide-app
  python3 install.py --launch
  python3 install.py --local
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main"
UA = "OnceHumanGuide-Installer/5.1"
SOURCE = Path(__file__).resolve().parent
DEFAULT_DIR = Path.cwd() / "once-human-guide-app"

CORE_FILES = [
    "version.json", "api_main.py", "updater.py", "install.py",
    "requirements.txt", "start.sh", "README.md",
]
DATA_JSON = [
    "deviations.json", "weapons.json", "armor.json", "mods.json", "bosses.json",
    "map_locations.json", "recipes.json", "materials.json", "scenarios.json",
    "quests.json", "events.json", "creatures.json", "npcs.json", "plants.json",
    "fish.json", "animals.json", "flowers.json",
]
OPTIONAL = ["database_full.json", "once_human_guide_ui_v4.html", "once_human_guide_app.html"]
MODULE_KEYS = [
    ("deviations", "deviations.json"), ("weapons", "weapons.json"), ("armor", "armor.json"),
    ("mods", "mods.json"), ("bosses", "bosses.json"), ("locations", "map_locations.json"),
    ("recipes", "recipes.json"), ("materials", "materials.json"), ("scenarios", "scenarios.json"),
    ("quests", "quests.json"), ("events", "events.json"), ("creatures", "creatures.json"),
    ("npcs", "npcs.json"), ("plants", "plants.json"), ("fish", "fish.json"),
    ("animals", "animals.json"), ("flowers", "flowers.json"),
]


def log(msg: str) -> None:
    print(msg, flush=True)


def download(url: str, dest: Path, timeout: int = 90) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            dest.write_bytes(resp.read())
        log(f"  ✓ {dest.name} ({dest.stat().st_size} B)")
        return True
    except Exception as e:
        log(f"  ✗ {dest.name}: {e}")
        return False


def fetch_file(name: str, dest_dir: Path, prefer_local: bool) -> bool:
    dest = dest_dir / name
    local = SOURCE / name
    if prefer_local and local.exists() and local.resolve() != dest.resolve():
        shutil.copy2(local, dest)
        log(f"  ✓ {name} (local copy)")
        return True
    if download(f"{RAW}/{name}", dest):
        return True
    if local.exists() and local.resolve() != dest.resolve():
        shutil.copy2(local, dest)
        log(f"  ✓ {name} (local fallback)")
        return True
    return False


def ensure_python() -> None:
    if sys.version_info < (3, 10):
        log(f"[install] Python 3.10+ required (found {sys.version})")
        sys.exit(1)


def pip_install(dest_dir: Path) -> None:
    req = dest_dir / "requirements.txt"
    if not req.exists():
        req.write_text("fastapi>=0.110.0\nuvicorn[standard]>=0.27.0\n", encoding="utf-8")
    log("[install] installing Python packages…")
    for cmd in (
        [sys.executable, "-m", "pip", "install", "--user", "-q", "-r", str(req)],
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(req)],
    ):
        try:
            subprocess.check_call(cmd)
            log("[install] pip OK")
            return
        except subprocess.CalledProcessError:
            continue
    log("[install] WARNING: pip failed. Later: python -m pip install -r requirements.txt")


def assemble_database(dest_dir: Path):
    full = dest_dir / "database_full.json"
    modules = {}
    for key, fname in MODULE_KEYS:
        fp = dest_dir / fname
        if fp.exists():
            try:
                modules[key] = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                pass
    if not modules:
        return full if full.exists() else None
    ver = "assembled"
    vp = dest_dir / "version.json"
    if vp.exists():
        try:
            ver = json.loads(vp.read_text(encoding="utf-8")).get("data_version", ver)
        except Exception:
            pass
    data = {"version": ver, **modules}
    full.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    n = sum(len(v) for v in modules.values() if isinstance(v, list))
    log(f"[install] assembled database_full.json ({len(modules)} modules, {n} records)")
    return full


def rebuild_sqlite(json_path: Path, db_path: Path) -> int:
    import sqlite3
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("CREATE TABLE data_versions (table_name TEXT PRIMARY KEY, version TEXT, updated_at TEXT)")
    c.execute("INSERT INTO data_versions VALUES ('all', ?, datetime('now'))", (data.get("version", "unknown"),))
    total = 0
    for key, rows in data.items():
        if key in ("version", "meta") or not isinstance(rows, list) or not rows:
            continue
        cols = list(rows[0].keys())
        c.execute(f'CREATE TABLE IF NOT EXISTS "{key}" (' + ", ".join(f'"{col}" TEXT' for col in cols) + ")")
        for row in rows:
            vals = [json.dumps(row.get(col), ensure_ascii=False) if isinstance(row.get(col), (list, dict)) else row.get(col) for col in cols]
            c.execute(f'INSERT INTO "{key}" VALUES (' + ",".join("?" * len(cols)) + ")", vals)
            total += 1
    conn.commit()
    conn.close()
    return total


def write_launchers(dest_dir: Path) -> None:
    sh = dest_dir / "start.sh"
    sh.write_text(
        "#!/usr/bin/env bash\nset -e\ncd \"$(dirname \"$0\")\"\n"
        "python3 -m pip install -q -r requirements.txt 2>/dev/null || true\n"
        "echo \"  Once Human Guide — http://127.0.0.1:8000/ui\"\n"
        "exec python3 -m uvicorn api_main:app --host 0.0.0.0 --port 8000\n",
        encoding="utf-8",
    )
    try:
        sh.chmod(sh.stat().st_mode | 0o111)
    except Exception:
        pass
    (dest_dir / "start.bat").write_text(
        "@echo off\r\ncd /d %~dp0\r\npython -m pip install -q -r requirements.txt\r\n"
        "echo   Once Human Guide — http://127.0.0.1:8000/ui\r\n"
        "python -m uvicorn api_main:app --host 127.0.0.1 --port 8000\r\npause\r\n",
        encoding="utf-8",
    )
    (dest_dir / "update.sh").write_text(
        "#!/usr/bin/env bash\ncd \"$(dirname \"$0\")\"\npython3 updater.py \"$@\"\n", encoding="utf-8"
    )
    try:
        (dest_dir / "update.sh").chmod((dest_dir / "update.sh").stat().st_mode | 0o111)
    except Exception:
        pass
    (dest_dir / "update.bat").write_text(
        "@echo off\r\ncd /d %~dp0\r\npython updater.py %*\r\npause\r\n", encoding="utf-8"
    )
    log("[install] wrote start.sh / start.bat / update.sh / update.bat")


def write_minimal_ui(dest_dir: Path) -> None:
    html = dest_dir / "once_human_guide_ui_v4.html"
    if html.exists() and html.stat().st_size > 1000:
        return
    html.write_text(
        "<!DOCTYPE html><html lang=cs><head><meta charset=utf-8><title>Once Human Guide</title></head>"
        "<body style='font-family:system-ui;background:#0b0f14;color:#cde;padding:2rem'>"
        "<h1>Once Human Guide</h1>"
        "<p><a style='color:#3cf' href='http://127.0.0.1:8000/ui'>Open app http://127.0.0.1:8000/ui</a></p>"
        "<p>Start: <code>./start.sh</code> or <code>start.bat</code></p></body></html>",
        encoding="utf-8",
    )
    log("[install] wrote minimal UI launcher")


def install(dest: Path, prefer_local: bool, launch: bool) -> int:
    ensure_python()
    dest = dest.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    log("\n══════════════════════════════════════")
    log("  Once Human Guide — Auto Installer")
    log("══════════════════════════════════════")
    log(f"  target: {dest}")
    log(f"  python: {sys.version.split()[0]}\n")
    log("[1/5] Downloading core files…")
    ok = sum(1 for n in CORE_FILES if fetch_file(n, dest, prefer_local))
    log("[2/5] Downloading game data…")
    ok += sum(1 for n in DATA_JSON if fetch_file(n, dest, prefer_local))
    log("[3/5] Optional assets…")
    for n in OPTIONAL:
        fetch_file(n, dest, prefer_local)
    log(f"[install] {ok} required files ready")
    log("[4/5] Python dependencies…")
    pip_install(dest)
    log("[5/5] Building database…")
    full = assemble_database(dest)
    if full and full.exists():
        n = rebuild_sqlite(full, dest / "once_human.db")
        log(f"[install] SQLite once_human.db ({n} rows)")
    write_launchers(dest)
    write_minimal_ui(dest)
    ver = {}
    if (dest / "version.json").exists():
        try:
            ver = json.loads((dest / "version.json").read_text(encoding="utf-8"))
        except Exception:
            pass
    log("\n══════════════════════════════════════")
    log("  INSTALL COMPLETE")
    log("══════════════════════════════════════")
    log(f"  app:  {ver.get('app_version', '?')}")
    log(f"  data: {ver.get('data_version', '?')}")
    log(f"  dir:  {dest}\n")
    log("  Start:  ./start.sh   or   start.bat")
    log("  Open:   http://127.0.0.1:8000/ui")
    log("  Update: python3 updater.py\n")
    if launch:
        log("[install] launching…")
        os.chdir(dest)
        os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"])
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Once Human Guide auto-installer")
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--from-github", action="store_true")
    ap.add_argument("--launch", action="store_true")
    args = ap.parse_args()
    prefer_local = args.local and not args.from_github
    try:
        sys.exit(install(args.dir, prefer_local, args.launch))
    except KeyboardInterrupt:
        log("\n[install] cancelled")
        sys.exit(130)


if __name__ == "__main__":
    main()
