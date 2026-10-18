"""Smoke tests for the Once Human Guide API and the SQLite builder.

Keeps the GitHub Actions "build" job (flake8 + pytest) meaningful without a
live server: everything runs against a throwaway DB in tmp_path.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

import api_main
import db_build


def test_routes_registered():
    paths = {route.path for route in api_main.app.routes}
    assert {
        "/",
        "/health",
        "/ui",
        "/stats",
        "/search",
        "/audit",
        "/integrity",
        "/version.json",
    }.issubset(paths)


def test_versions_loaded():
    assert api_main.API_VERSION
    assert api_main.DATA_VERSION


def test_fts_query_is_sanitized():
    assert api_main._fts_query("soc r?!") == "soc* r*"
    assert api_main._fts_query("???") == '""'


def test_build_creates_audit_and_catalog(tmp_path):
    db_path = tmp_path / "once_human.db"
    result = db_build.build(db_path)
    assert result["records"] == 372
    assert result["links"] > 0
    assert result["issues"] > 0

    conn = sqlite3.connect(db_path)
    try:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
        fts = conn.execute("SELECT COUNT(*) FROM entities_fts").fetchone()[0]
        issues = conn.execute("SELECT COUNT(*) FROM data_issues").fetchone()[0]
    finally:
        conn.close()

    assert {"entities", "entities_fts", "links", "data_issues"}.issubset(names)
    assert fts == result["records"]
    assert issues == result["issues"]


def test_list_filters(tmp_path, monkeypatch):
    db_path = tmp_path / "once_human.db"
    db_build.build(db_path)
    monkeypatch.setattr(api_main, "DB_PATH", db_path)

    all_weapons = api_main.fetch_all("weapons", limit=1000)
    assert all_weapons
    rarity = all_weapons[0]["rarity"]
    filtered = api_main.fetch_all("weapons", limit=1000, rarity=rarity.upper())
    assert filtered
    assert all(row["rarity"].lower() == rarity.lower() for row in filtered)
    assert len(filtered) <= len(all_weapons)

    mods = api_main.fetch_all("mods", limit=1000, slot=api_main.fetch_all("mods", limit=1)[0]["slot"])
    assert mods

    with pytest.raises(Exception):
        api_main.fetch_all("does_not_exist")


def test_search_prefers_fts(tmp_path, monkeypatch):
    db_path = tmp_path / "once_human.db"
    db_build.build(db_path)
    monkeypatch.setattr(api_main, "DB_PATH", db_path)

    result = api_main.search(q="socr", limit=10)
    assert result["mode"] == "fts"
    assert result["count"] >= 1


def test_release_files_exist():
    meta = json.loads((api_main.BASE / "version.json").read_text(encoding="utf-8"))
    missing = [name for name in meta["files"] if not (api_main.BASE / name).exists()]
    assert missing == []


def test_release_version_is_the_single_source():
    """version.json, the shell pack, the shell's asset URLs and the service worker
    cache must all carry the same release."""
    meta = json.loads((api_main.BASE / "version.json").read_text(encoding="utf-8"))
    version = meta["data_version"]
    pack = (api_main.BASE / "ohg_data.js").read_text(encoding="utf-8")
    assert '"version": "' + version + '"' in pack
    assert '"entities": ' + str(meta["records"]) in pack
    sw = (api_main.BASE / "ohg_sw.js").read_text(encoding="utf-8")
    assert meta["sw_cache"] in sw
    assert ("ohg-" + version) in meta["sw_cache"]
    shell = (api_main.BASE / "once_human_guide_v19.html").read_text(encoding="utf-8")
    assert 'ohg_data.js?v=' + version in shell
    assert 'modules/ohg_runtime.js?v=' + version in shell


def test_build_stores_manifest_version_and_links(tmp_path):
    db_path = tmp_path / "once_human.db"
    result = db_build.build(db_path)
    conn = sqlite3.connect(db_path)
    try:
        version = conn.execute("SELECT version FROM data_versions WHERE table_name='all'").fetchone()[0]
        links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        covered = conn.execute(
            """SELECT COUNT(*) FROM entities WHERE EXISTS (
                   SELECT 1 FROM links l
                   WHERE (l.src_table=entities.table_name AND l.src_id=entities.id)
                      OR (l.dst_table=entities.table_name AND l.dst_id=entities.id))"""
        ).fetchone()[0]
        unresolved = conn.execute(
            "SELECT COUNT(*) FROM data_issues WHERE code='unresolved_ingredient'"
        ).fetchone()[0]
    finally:
        conn.close()
    meta = json.loads((api_main.BASE / "version.json").read_text(encoding="utf-8"))
    assert version == meta["data_version"]
    assert result["links"] == links
    assert links >= 120
    assert covered >= 100
    # Ingredients the pack does not contain at all — a pack-authoring backlog, not a bug.
    assert unresolved <= 30


def test_label_variants_resolve_bundled_names():
    keys = db_build._label_keys("Metal Scraps / Ingots")
    assert "metal scraps" in keys and "metal scraps / ingots" == keys[0]


def test_admin_endpoints_are_closed_without_a_token(tmp_path, monkeypatch):
    monkeypatch.delenv("OHG_ADMIN_TOKEN", raising=False)
    monkeypatch.setattr(api_main, "TOKEN_FILE", tmp_path / ".admin_token")
    assert api_main.admin_allowed(None) is False
    assert api_main.admin_allowed("whatever") is False


def test_admin_token_must_match(tmp_path, monkeypatch):
    monkeypatch.delenv("OHG_ADMIN_TOKEN", raising=False)
    token_file = tmp_path / ".admin_token"
    token_file.write_text("file-token\n", encoding="utf-8")
    monkeypatch.setattr(api_main, "TOKEN_FILE", token_file)
    assert api_main.admin_allowed("file-token") is True
    assert api_main.admin_allowed("wrong") is False
    monkeypatch.setenv("OHG_ADMIN_TOKEN", "env-token")
    assert api_main.admin_allowed("env-token") is True
    assert api_main.admin_allowed("file-token") is False
