"""Smoke test: pack builds a searchable catalog without touching user data."""
import sqlite3
from pathlib import Path

import db_build


def test_build_counts(tmp_path: Path):
    out = db_build.build(tmp_path / "once_human.db")
    assert out["records"] == 372
    assert out["issues"] == 0
    assert out["links"] >= 17
    conn = sqlite3.connect(out["db"])
    fts = conn.execute("SELECT COUNT(*) FROM entities_fts").fetchone()[0]
    aliases = conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
    schema = conn.execute("SELECT version FROM data_versions WHERE table_name='schema'").fetchone()[0]
    conn.close()
    assert fts == 372
    assert aliases >= 300
    assert schema.startswith("5.5")
