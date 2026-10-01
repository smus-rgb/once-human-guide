#!/usr/bin/env python3
"""Build SQLite DB + minimal UI from the bundled JSON modules (Base44 dev setup)."""
from pathlib import Path
from install import assemble_database, rebuild_sqlite, write_minimal_ui

base = Path(__file__).resolve().parent
full = assemble_database(base)
if full and full.exists():
    n = rebuild_sqlite(full, base / "once_human.db")
    print(f"[base44] SQLite once_human.db built ({n} rows)")
else:
    print("[base44] WARNING: could not assemble database_full.json")
write_minimal_ui(base)
print("[base44] UI ready")
