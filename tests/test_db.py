import sqlite3
from pathlib import Path

import db_build


def test_build_replaces_db_and_indexes_aliases(tmp_path: Path):
    db = tmp_path / "once_human.db"
    report = db_build.build(db)
    assert report["records"] == 372
    assert db.exists()
    assert not Path(str(db) + ".tmp").exists()
    conn = sqlite3.connect(db)
    assert conn.execute("select count(*) from aliases").fetchone()[0] > 0
    assert conn.execute("select count(*) from entities_fts where entities_fts match 'zbran*'").fetchone()[0] > 0
    conn.close()
