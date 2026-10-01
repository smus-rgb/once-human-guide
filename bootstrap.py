#!/usr/bin/env python3
"""Once Human Guide — one-file bootstrap

Download ONLY this file, then run:
  python3 bootstrap.py

It downloads install.py from GitHub and runs a full automatic install.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

RAW_INSTALL = (
    "https://raw.githubusercontent.com/smus-rgb/once-human-guide/main/install.py"
)
UA = "OnceHumanGuide-Bootstrap/5.1"


def main() -> int:
    print("Once Human Guide — bootstrap")
    print(f"  fetching {RAW_INSTALL}")
    req = urllib.request.Request(RAW_INSTALL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        code = resp.read()
    dest_dir = Path.cwd() / "once-human-guide-app"
    dest_dir.mkdir(parents=True, exist_ok=True)
    installer = dest_dir / "install.py"
    installer.write_bytes(code)
    print(f"  saved {installer}")
    print("  running installer…")
    print()
    # Default: GitHub install into once-human-guide-app next to cwd
    cmd = [sys.executable, str(installer), "--dir", str(dest_dir)]
    if "--launch" in sys.argv:
        cmd.append("--launch")
    return subprocess.call(cmd)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"bootstrap failed: {e}")
        raise SystemExit(1)
