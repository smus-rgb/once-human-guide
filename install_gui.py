#!/usr/bin/env python3
"""Once Human Guide — graphical installer (Start button)

Requires Python 3.10+ with tkinter (included on most desktops).

  python3 install_gui.py
"""
from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path
from tkinter import (
    BooleanVar,
    Button,
    Checkbutton,
    Entry,
    Frame,
    Label,
    StringVar,
    Tk,
    messagebox,
    scrolledtext,
)

# ── theme ────────────────────────────────────────────────────────────────────
BG = "#0b0f14"
PANEL = "#121820"
FG = "#c8d6e5"
ACCENT = "#2ee6a6"
ACCENT_DIM = "#1a9e72"
WARN = "#f0a030"
ERR = "#e05050"
MUTED = "#6a7a8a"
FONT = ("Segoe UI", 11) if sys.platform == "win32" else ("Helvetica", 11)
FONT_B = ("Segoe UI", 14, "bold") if sys.platform == "win32" else ("Helvetica", 14, "bold")
FONT_LOG = ("Consolas", 9) if sys.platform == "win32" else ("Courier", 9)

RAW = "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main"
UA = "OnceHumanGuide-GUI-Installer/5.2"
SOURCE = Path(__file__).resolve().parent

CORE = [
    "version.json",
    "api_main.py",
    "updater.py",
    "install.py",
    "requirements.txt",
    "start.sh",
    "README.md",
]
DATA = [
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
OPTIONAL = ["database_full.json", "once_human_guide_ui_v4.html"]
MODULES = [
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


class InstallerGUI:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Once Human Guide — Installer")
        self.root.configure(bg=BG)
        self.root.minsize(520, 480)
        self.root.geometry("560x560")

        self.dir_var = StringVar(value=str(Path.home() / "once-human-guide-app"))
        self.launch_var = BooleanVar(value=True)
        self.busy = False
        self.server_proc: subprocess.Popen | None = None

        self._build()

    def _build(self) -> None:
        head = Frame(self.root, bg=BG)
        head.pack(fill="x", padx=20, pady=(18, 8))
        Label(
            head,
            text="ONCE HUMAN GUIDE",
            font=FONT_B,
            fg=ACCENT,
            bg=BG,
        ).pack(anchor="w")
        Label(
            head,
            text="Automatic installer · downloads data from GitHub · builds database",
            font=FONT,
            fg=MUTED,
            bg=BG,
        ).pack(anchor="w", pady=(2, 0))

        body = Frame(self.root, bg=PANEL, highlightbackground="#1e2a36", highlightthickness=1)
        body.pack(fill="both", expand=True, padx=20, pady=8)

        Label(body, text="Install folder", font=FONT, fg=MUTED, bg=PANEL).pack(
            anchor="w", padx=14, pady=(12, 2)
        )
        row = Frame(body, bg=PANEL)
        row.pack(fill="x", padx=14)
        self.dir_entry = Entry(
            row,
            textvariable=self.dir_var,
            font=FONT,
            bg="#0b0f14",
            fg=FG,
            insertbackground=FG,
            relief="flat",
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        Checkbutton(
            body,
            text="Start app after install",
            variable=self.launch_var,
            font=FONT,
            fg=FG,
            bg=PANEL,
            activebackground=PANEL,
            activeforeground=FG,
            selectcolor="#0b0f14",
            highlightthickness=0,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        self.status = Label(body, text="Ready", font=FONT, fg=MUTED, bg=PANEL)
        self.status.pack(anchor="w", padx=14, pady=(4, 6))

        self.log = scrolledtext.ScrolledText(
            body,
            height=12,
            font=FONT_LOG,
            bg="#080c10",
            fg=FG,
            insertbackground=FG,
            relief="flat",
            state="disabled",
            wrap="word",
        )
        self.log.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        btns = Frame(self.root, bg=BG)
        btns.pack(fill="x", padx=20, pady=(4, 16))

        self.btn_start = Button(
            btns,
            text="  ▶  START  ",
            font=FONT_B,
            fg="#06140f",
            bg=ACCENT,
            activebackground=ACCENT_DIM,
            activeforeground="#06140f",
            relief="flat",
            cursor="hand2",
            command=self.on_start,
            padx=16,
            pady=10,
        )
        self.btn_start.pack(side="left")

        self.btn_open = Button(
            btns,
            text=" Open UI ",
            font=FONT,
            fg=FG,
            bg="#1a2430",
            activebackground="#243040",
            activeforeground=FG,
            relief="flat",
            cursor="hand2",
            command=self.open_ui,
            state="disabled",
            padx=12,
            pady=10,
        )
        self.btn_open.pack(side="left", padx=(10, 0))

        Button(
            btns,
            text=" Quit ",
            font=FONT,
            fg=MUTED,
            bg=BG,
            activebackground=PANEL,
            activeforeground=FG,
            relief="flat",
            cursor="hand2",
            command=self.on_quit,
            padx=12,
            pady=10,
        ).pack(side="right")

    def append_log(self, msg: str) -> None:
        def _do() -> None:
            self.log.configure(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")

        self.root.after(0, _do)

    def set_status(self, text: str, color: str = MUTED) -> None:
        self.root.after(0, lambda: self.status.configure(text=text, fg=color))

    def on_start(self) -> None:
        if self.busy:
            return
        dest = Path(self.dir_var.get().strip()).expanduser()
        if not dest.parts:
            messagebox.showerror("Error", "Enter install folder")
            return
        self.busy = True
        self.btn_start.configure(state="disabled", bg=ACCENT_DIM)
        self.btn_open.configure(state="disabled")
        self.set_status("Installing…", ACCENT)
        threading.Thread(target=self._install_worker, args=(dest,), daemon=True).start()

    def _download(self, name: str, dest_dir: Path) -> bool:
        dest = dest_dir / name
        local = SOURCE / name
        url = f"{RAW}/{name}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as resp:
                dest.write_bytes(resp.read())
            self.append_log(f"  ✓ {name}")
            return True
        except Exception:
            if local.exists():
                shutil.copy2(local, dest)
                self.append_log(f"  ✓ {name} (local)")
                return True
            self.append_log(f"  ✗ {name}")
            return False

    def _assemble_db(self, dest: Path) -> Path | None:
        modules: dict = {}
        for key, fname in MODULES:
            fp = dest / fname
            if fp.exists():
                try:
                    modules[key] = json.loads(fp.read_text(encoding="utf-8"))
                except Exception:
                    pass
        if not modules:
            full = dest / "database_full.json"
            return full if full.exists() else None
        ver = "assembled"
        vp = dest / "version.json"
        if vp.exists():
            try:
                ver = json.loads(vp.read_text(encoding="utf-8")).get("data_version", ver)
            except Exception:
                pass
        full = dest / "database_full.json"
        full.write_text(
            json.dumps({"version": ver, **modules}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        n = sum(len(v) for v in modules.values() if isinstance(v, list))
        self.append_log(f"  DB assembled: {len(modules)} modules, {n} records")
        return full

    def _rebuild_sqlite(self, json_path: Path, db_path: Path) -> int:
        import sqlite3

        data = json.loads(json_path.read_text(encoding="utf-8"))
        if db_path.exists():
            db_path.unlink()
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute(
            "CREATE TABLE data_versions (table_name TEXT PRIMARY KEY, version TEXT, updated_at TEXT)"
        )
        c.execute(
            "INSERT INTO data_versions VALUES ('all', ?, datetime('now'))",
            (data.get("version", "unknown"),),
        )
        total = 0
        for key, rows in data.items():
            if key in ("version", "meta") or not isinstance(rows, list) or not rows:
                continue
            cols = list(rows[0].keys())
            c.execute(
                f'CREATE TABLE IF NOT EXISTS "{key}" ('
                + ", ".join(f'"{col}" TEXT' for col in cols)
                + ")"
            )
            for row in rows:
                vals = [
                    json.dumps(row.get(col), ensure_ascii=False)
                    if isinstance(row.get(col), (list, dict))
                    else row.get(col)
                    for col in cols
                ]
                c.execute(
                    f'INSERT INTO "{key}" VALUES (' + ",".join("?" * len(cols)) + ")",
                    vals,
                )
                total += 1
        conn.commit()
        conn.close()
        return total

    def _write_launchers(self, dest: Path) -> None:
        sh = dest / "start.sh"
        sh.write_text(
            "#!/usr/bin/env bash\nset -e\ncd \"$(dirname \"$0\")\"\n"
            "python3 -m pip install -q -r requirements.txt 2>/dev/null || true\n"
            "echo \"  Once Human Guide — http://127.0.0.1:8000/ui\"\n"
            "exec python3 -m uvicorn api_main:app --host 127.0.0.1 --port 8000\n",
            encoding="utf-8",
        )
        try:
            sh.chmod(sh.stat().st_mode | 0o111)
        except Exception:
            pass
        (dest / "start.bat").write_text(
            "@echo off\r\ncd /d %~dp0\r\n"
            "python -m pip install -q -r requirements.txt\r\n"
            "echo   Once Human Guide — http://127.0.0.1:8000/ui\r\n"
            "python -m uvicorn api_main:app --host 127.0.0.1 --port 8000\r\n"
            "pause\r\n",
            encoding="utf-8",
        )

    def _install_worker(self, dest: Path) -> None:
        try:
            if sys.version_info < (3, 10):
                raise RuntimeError("Python 3.10+ required")
            dest.mkdir(parents=True, exist_ok=True)
            self.append_log(f"Target: {dest}")
            self.append_log("— Core files —")
            ok = 0
            for name in CORE:
                if self._download(name, dest):
                    ok += 1
            self.append_log("— Game data —")
            for name in DATA:
                if self._download(name, dest):
                    ok += 1
            self.append_log("— Optional —")
            for name in OPTIONAL:
                self._download(name, dest)
            self.append_log(f"Files ready: {ok}")

            self.append_log("— pip packages —")
            req = dest / "requirements.txt"
            if not req.exists():
                req.write_text(
                    "fastapi>=0.110.0\nuvicorn[standard]>=0.27.0\n", encoding="utf-8"
                )
            pip_ok = False
            for cmd in (
                [sys.executable, "-m", "pip", "install", "--user", "-q", "-r", str(req)],
                [sys.executable, "-m", "pip", "install", "-q", "-r", str(req)],
            ):
                try:
                    subprocess.check_call(cmd)
                    pip_ok = True
                    self.append_log("  ✓ pip OK")
                    break
                except subprocess.CalledProcessError:
                    continue
            if not pip_ok:
                self.append_log("  ! pip failed — install later manually")

            self.append_log("— Database —")
            full = self._assemble_db(dest)
            if full and full.exists():
                n = self._rebuild_sqlite(full, dest / "once_human.db")
                self.append_log(f"  ✓ SQLite ({n} rows)")
            else:
                self.append_log("  ! no data modules")

            self._write_launchers(dest)
            self.append_log("— Launchers written —")
            self.append_log("")
            self.append_log("INSTALL COMPLETE")
            self.append_log("UI: http://127.0.0.1:8000/ui")

            self.root.after(0, lambda: self._on_done(dest, success=True))
        except Exception as e:
            self.append_log(f"ERROR: {e}")
            self.root.after(0, lambda: self._on_done(dest, success=False, err=str(e)))

    def _on_done(self, dest: Path, success: bool, err: str = "") -> None:
        self.busy = False
        self.btn_start.configure(state="normal", bg=ACCENT)
        if success:
            self.set_status(f"Installed → {dest}", ACCENT)
            self.btn_open.configure(state="normal")
            if self.launch_var.get():
                self._start_server(dest)
        else:
            self.set_status(f"Failed: {err}", ERR)
            messagebox.showerror("Install failed", err or "Unknown error")

    def _start_server(self, dest: Path) -> None:
        self.append_log("Starting server…")
        try:
            creation = 0
            if sys.platform == "win32":
                creation = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            self.server_proc = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "api_main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                ],
                cwd=str(dest),
                creationflags=creation,
            )
            self.set_status("Server running · http://127.0.0.1:8000/ui", ACCENT)
            self.root.after(1500, self.open_ui)
        except Exception as e:
            self.append_log(f"Server start failed: {e}")
            self.set_status("Install OK — start manually with start.bat / start.sh", WARN)

    def open_ui(self) -> None:
        url = "http://127.0.0.1:8000/ui"
        try:
            webbrowser.open(url)
        except Exception:
            messagebox.showinfo("Open browser", url)

    def on_quit(self) -> None:
        if self.server_proc and self.server_proc.poll() is None:
            if messagebox.askyesno("Quit", "Stop server and quit?"):
                try:
                    self.server_proc.terminate()
                except Exception:
                    pass
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("tkinter not available. Use: python3 install.py")
        print("On Debian/Ubuntu: sudo apt install python3-tk")
        sys.exit(1)
    InstallerGUI().run()


if __name__ == "__main__":
    main()
