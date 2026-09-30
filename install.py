#!/usr/bin/env python3
"""Once Human Guide — installer

Sets up a local install directory, copies/downloads app files, installs Python
deps, builds SQLite DB, and optionally launches the API.

Usage:
  python install.py                  # install into ./once-human-guide-app
  python install.py --dir ~/oh-guide
  python install.py --launch         # install + start API
  python install.py --from-github    # fetch files from GitHub instead of local
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

SOURCE = Path(__file__).resolve().parent
DEFAULT_DIR = Path.cwd() / "once-human-guide-app"
RAW = "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main"

CORE_FILES = [
    "version.json",
    "database_full.json",
    "once_human_guide_ui_v4.html",
    "api_main.py",
    "updater.py",
    "install.py",
    "requirements.txt",
    "start.sh",
    "README.md",
]

DATA_JSON = [
    "deviations.json", "weapons.json", "armor.json", "mods.json", "bosses.json",
    "map_locations.json", "recipes.json", "materials.json", "scenarios.json",
    "quests.json", "events.json", "creatures.json", "npcs.json", "plants.json",
    "fish.json", "animals.json", "flowers.json",
]


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "OnceHumanGuide-Installer/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())
    print(f"  downloaded {dest.name}")


def copy_or_fetch(name: str, dest_dir: Path, from_github: bool) -> bool:
    dest = dest_dir / name
    src = SOURCE / name
    if not from_github and src.exists():
        shutil.copy2(src, dest)
        print(f"  copied {name}")
        return True
    try:
        download(f"{RAW}/{name}", dest)
        return True
    except Exception as e:
        print(f"  missing {name}: {e}")
        return False


def pip_install(dest_dir: Path) -> None:
    req = dest_dir / "requirements.txt"
    if not req.exists():
        print("[install] no requirements.txt — skip pip")
        return
    print("[install] pip install -r requirements.txt")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(req)],
    )


def rebuild_db(dest_dir: Path) -> None:
    updater = dest_dir / "updater.py"
    full = dest_dir / "database_full.json"
    if not full.exists():
        print("[install] no database_full.json — skip SQLite")
        return
    sys.path.insert(0, str(dest_dir))
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("updater", updater)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        n = mod.rebuild_sqlite(full, dest_dir / "once_human.db")
        print(f"[install] SQLite ready ({n} rows)")
    except Exception as e:
        print(f"[install] SQLite rebuild via updater failed: {e}")
        import sqlite3
        data = json.loads(full.read_text(encoding="utf-8"))
        dbp = dest_dir / "once_human.db"
        if dbp.exists():
            dbp.unlink()
        conn = sqlite3.connect(str(dbp))
        c = conn.cursor()
        c.execute("CREATE TABLE data_versions (table_name TEXT, version TEXT, updated_at TEXT)")
        c.execute("INSERT INTO data_versions VALUES ('all',?,datetime('now'))", (data.get("version", "?"),))
        for table, rows in data.items():
            if not isinstance(rows, list) or not rows:
                continue
            cols = list(rows[0].keys())
            col_sql = ", ".join(f'"{c}" TEXT' for c in cols)
            c.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_sql})')
            for row in rows:
                vals = [json.dumps(row[c], ensure_ascii=False) if isinstance(row.get(c), list) else row.get(c) for c in cols]
                c.execute(f'INSERT INTO "{table}" VALUES ({ ",".join("?"*len(cols)) })', vals)
        conn.commit()
        conn.close()
        print("[install] SQLite fallback build done")


def write_launcher(dest_dir: Path) -> None:
    if os.name == "nt":
        bat = dest_dir / "start.bat"
        bat.write_text(
            "@echo off\n"
            "cd /d %~dp0\n"
            "python -m pip install -q -r requirements.txt\n"
            "echo UI  http://127.0.0.1:8000/ui\n"
            "python -m uvicorn api_main:app --host 127.0.0.1 --port 8000\n",
            encoding="utf-8",
        )
        print("  wrote start.bat")
    sh = dest_dir / "start.sh"
    if not sh.exists():
        sh.write_text(
            "#!/usr/bin/env bash\n"
            "cd \"$(dirname \"$0\")\"\n"
            "python3 -m pip install -q -r requirements.txt 2>/dev/null || true\n"
            "echo UI  http://127.0.0.1:8000/ui\n"
            "exec python3 -m uvicorn api_main:app --host 0.0.0.0 --port 8000\n",
            encoding="utf-8",
        )
    try:
        sh.chmod(sh.stat().st_mode | 0o111)
    except Exception:
        pass
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
    print("  wrote start.sh / update.sh")


def install(dest: Path, from_github: bool, launch: bool) -> int:
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    print(f"[install] target: {dest}")
    print(f"[install] source: {'GitHub' if from_github else SOURCE}")

    ok = 0
    for name in CORE_FILES + DATA_JSON:
        if copy_or_fetch(name, dest, from_github):
            ok += 1
    print(f"[install] {ok} files in place")

    pip_install(dest)
    rebuild_db(dest)
    write_launcher(dest)

    ver = {}
    vp = dest / "version.json"
    if vp.exists():
        ver = json.loads(vp.read_text(encoding="utf-8"))
    print()
    print("=== Once Human Guide installed ===")
    print(f"  app:  {ver.get('app_version', '?')}")
    print(f"  data: {ver.get('data_version', '?')}")
    print(f"  dir:  {dest}")
    print()
    print("Offline UI:")
    print(f"  open {dest / 'once_human_guide_ui_v4.html'}")
    print("API server:")
    print(f"  cd {dest} && ./start.sh")
    print("  → http://127.0.0.1:8000/ui")
    print("Update data:")
    print(f"  cd {dest} && python3 updater.py")
    print()

    if launch:
        print("[install] launching API…")
        os.chdir(dest)
        os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "api_main:app", "--host", "0.0.0.0", "--port", "8000"])
    return 0


def main():
    ap = argparse.ArgumentParser(description="Install Once Human Guide")
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR, help="Install directory")
    ap.add_argument("--from-github", action="store_true", help="Download from GitHub raw")
    ap.add_argument("--launch", action="store_true", help="Start API after install")
    args = ap.parse_args()
    try:
        sys.exit(install(args.dir, args.from_github, args.launch))
    except subprocess.CalledProcessError as e:
        print(f"[install] command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
