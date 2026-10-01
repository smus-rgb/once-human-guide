#!/usr/bin/env python3
"""Once Human Guide — automatic installer (bootstrap)

One command installs everything:
  - downloads all app files from GitHub
  - installs Python dependencies (fastapi, uvicorn)
  - builds SQLite database from module JSON
  - creates start scripts (start.sh / start.bat)
  - optionally launches the app

Usage:
  python3 install.py
  python3 install.py --dir ~/once-human-guide-app
  python3 install.py --launch
  python3 install.py --local          # prefer files next to this script

Requires: Python 3.10+
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main"
UA = "OnceHumanGuide-Installer/5.2"
SOURCE = Path(__file__).resolve().parent
DEFAULT_DIR = Path.cwd() / "once-human-guide-app"

CORE_FILES = [
    "version.json",
    "api_main.py",
    "db_engine.py",
    "updater.py",
    "install.py",
    "requirements.txt",
    "start.sh",
    "README.md",
]

DATA_JSON = [
    "deviations.json",
    "weapons.json",
    "armor.json",
    "mods.json",
    "bosses.json",
    "map_locations.json",
    "recipes.json",
    "materials.json",
    "scenarios.json",
    "quests.json",
    "events.json",
    "creatures.json",
    "npcs.json",
    "plants.json",
    "fish.json",
    "animals.json",
    "flowers.json",
]

OPTIONAL = [
    "database_full.json",
    "once_human_guide_v19.html",
    "once_human_guide_v18.html",
    "ohg_data.js",
    "ohg_sw.js",
    "modules/ohg_runtime.js",
    "modules/ohg_map.js",
    "modules/ohg_builds.js",
    "modules/ohg_pack_channel.js",
    "once_human_guide_ui_v4.html",
    "once_human_guide_app.html",
    "Once_Human_Guide_v18_Modular_System.md",
    "CHANGELOG.md",
]

MODULE_KEYS = [
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
    dest.parent.mkdir(parents=True, exist_ok=True)
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
        log("[install] wrote default requirements.txt")
    log("[install] installing Python packages…")
    attempts = [
        [sys.executable, "-m", "pip", "install", "--user", "-q", "-r", str(req)],
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(req)],
    ]
    for cmd in attempts:
        try:
            subprocess.check_call(cmd)
            log("[install] pip OK")
            return
        except subprocess.CalledProcessError:
            continue
    log("[install] WARNING: pip failed (network?). Install later with:")
    log(f"  {sys.executable} -m pip install -r {req}")


def assemble_database(dest_dir: Path) -> Path | None:
    full = dest_dir / "database_full.json"
    modules: dict = {}
    for key, fname in MODULE_KEYS:
        fp = dest_dir / fname
        if fp.exists():
            try:
                modules[key] = json.loads(fp.read_text(encoding="utf-8"))
            except Exception as e:
                log(f"  warn: {fname}: {e}")
    if not modules and full.exists():
        return full
    if not modules:
        return None
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
    """Shared schema (indexes + FTS + entity_index) via db_engine."""
    from db_engine import rebuild_sqlite as _rebuild
    return _rebuild(json_path, db_path)


def write_launchers(dest_dir: Path) -> None:
    sh = dest_dir / "start.sh"
    sh.write_text(
        "#!/usr/bin/env bash\n"
        "set -e\n"
        "cd \"$(dirname \"$0\")\"\n"
        "python3 -m pip install -q -r requirements.txt 2>/dev/null || true\n"
        "echo \"\"\n"
        "echo \"  Once Human Guide\"\n"
        "echo \"  UI:  http://127.0.0.1:8000/ui\"\n"
        "echo \"  API: http://127.0.0.1:8000/docs\"\n"
        "echo \"  Offline: open once_human_guide_ui_v4.html (if present)\"\n"
        "echo \"\"\n"
        "exec python3 -m uvicorn api_main:app --host 0.0.0.0 --port 8000\n",
        encoding="utf-8",
    )
    try:
        sh.chmod(sh.stat().st_mode | 0o111)
    except Exception:
        pass

    bat = dest_dir / "start.bat"
    bat.write_text(
        "@echo off\r\n"
        "cd /d %~dp0\r\n"
        "python -m pip install -q -r requirements.txt\r\n"
        "echo.\r\n"
        "echo   Once Human Guide\r\n"
        "echo   UI:  http://127.0.0.1:8000/ui\r\n"
        "echo   API: http://127.0.0.1:8000/docs\r\n"
        "echo.\r\n"
        "python -m uvicorn api_main:app --host 127.0.0.1 --port 8000\r\n"
        "pause\r\n",
        encoding="utf-8",
    )

    upd = dest_dir / "update.sh"
    upd.write_text(
        "#!/usr/bin/env bash\n"
        "cd \"$(dirname \"$0\")\"\n"
        "python3 updater.py \"$@\"\n",
        encoding="utf-8",
    )
    try:
        upd.chmod(upd.stat().st_mode | 0o111)
    except Exception:
        pass

    updbat = dest_dir / "update.bat"
    updbat.write_text(
        "@echo off\r\n"
        "cd /d %~dp0\r\n"
        "python updater.py %*\r\n"
        "pause\r\n",
        encoding="utf-8",
    )
    log("[install] wrote start.sh, start.bat, update.sh, update.bat")


def write_minimal_ui(dest_dir: Path) -> None:
    """If SPA HTML was not downloaded, create a simple launcher page."""
    html = dest_dir / "once_human_guide_ui_v4.html"
    if html.exists() and html.stat().st_size > 1000:
        return
    page = """<!DOCTYPE html>
<html lang="cs"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Once Human Guide</title>
<style>
body{font-family:system-ui,sans-serif;background:#0b0f14;color:#cde;margin:0;padding:2rem}
a{color:#3cf} .card{max-width:40rem;margin:auto;border:1px solid #234;padding:1.5rem;border-radius:12px}
h1{color:#5ef} code{background:#123;padding:.2rem .4rem;border-radius:4px}
</style></head><body><div class="card">
<h1>Once Human Guide</h1>
<p>Offline SPA HTML is optional. Use the API UI:</p>
<p><a href="http://127.0.0.1:8000/ui">Open app at http://127.0.0.1:8000/ui</a></p>
<p>Start server: <code>./start.sh</code> or <code>start.bat</code></p>
<p>Update data: <code>python3 updater.py</code></p>
</div></body></html>
"""
    html.write_text(page, encoding="utf-8")
    log("[install] wrote minimal UI launcher HTML")


def install(dest: Path, prefer_local: bool, launch: bool) -> int:
    ensure_python()
    dest = dest.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    log("")
    log("══════════════════════════════════════")
    log("  Once Human Guide — Auto Installer")
    log("══════════════════════════════════════")
    log(f"  target:  {dest}")
    log(f"  source:  {'local+GitHub' if prefer_local else 'GitHub'}")
    log(f"  python:  {sys.version.split()[0]}")
    log("")

    log("[1/5] Downloading core files…")
    ok = 0
    for name in CORE_FILES:
        if fetch_file(name, dest, prefer_local):
            ok += 1

    log("[2/5] Downloading game data…")
    for name in DATA_JSON:
        if fetch_file(name, dest, prefer_local):
            ok += 1

    log("[3/5] Optional assets (UI / full DB)…")
    for name in OPTIONAL:
        fetch_file(name, dest, prefer_local)

    log(f"[install] {ok} required files ready")

    log("[4/5] Python dependencies…")
    pip_install(dest)

    log("[5/5] Building database…")
    full = assemble_database(dest)
    if full and full.exists():
        n = rebuild_sqlite(full, dest / "once_human.db")
        log(f"[install] SQLite once_human.db ({n} rows)")
    else:
        log("[install] WARNING: no data modules — DB empty")

    write_launchers(dest)
    write_minimal_ui(dest)

    # ensure updater exists for later updates
    if not (dest / "updater.py").exists():
        fetch_file("updater.py", dest, prefer_local)

    ver = {}
    vp = dest / "version.json"
    if vp.exists():
        try:
            ver = json.loads(vp.read_text(encoding="utf-8"))
        except Exception:
            pass

    log("")
    log("══════════════════════════════════════")
    log("  INSTALL COMPLETE")
    log("══════════════════════════════════════")
    log(f"  app:   {ver.get('app_version', '?')}")
    log(f"  data:  {ver.get('data_version', '?')}")
    log(f"  dir:   {dest}")
    log("")
    log("  Start:")
    if os.name == "nt":
        log(f"    cd /d {dest}")
        log("    start.bat")
    else:
        log(f"    cd {dest}")
        log("    ./start.sh")
    log("")
    log("  Then open:  http://127.0.0.1:8000/ui")
    log("  Update:     python3 updater.py")
    log("")

    if launch:
        log("[install] launching server…")
        os.chdir(dest)
        os.execv(
            sys.executable,
            [
                sys.executable,
                "-m",
                "uvicorn",
                "api_main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
        )
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Once Human Guide — automatic installer (downloads from GitHub)"
    )
    ap.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_DIR,
        help=f"Install directory (default: {DEFAULT_DIR})",
    )
    ap.add_argument(
        "--local",
        action="store_true",
        help="Prefer files next to install.py, then GitHub",
    )
    ap.add_argument(
        "--from-github",
        action="store_true",
        help="Force GitHub download (default behavior)",
    )
    ap.add_argument(
        "--launch",
        action="store_true",
        help="Start API server after install",
    )
    args = ap.parse_args()
    prefer_local = args.local and not args.from_github
    try:
        sys.exit(install(args.dir, prefer_local, args.launch))
    except subprocess.CalledProcessError as e:
        log(f"[install] failed: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        log("\n[install] cancelled")
        sys.exit(130)


if __name__ == "__main__":
    main()
