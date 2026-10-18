"""Smoke tests for the Once Human Guide API and the SQLite builder.

Keeps the GitHub Actions "build" job (flake8 + pytest) meaningful without a
live server: everything runs against a throwaway DB in tmp_path.
"""
from __future__ import annotations

import sqlite3

import pytest

import api_main
import db_build


def test_routes_registered():
    paths = {route.path for route in api_main.app.routes}
    assert {"/", "/health", "/ui", "/stats", "/search", "/audit", "/integrity"}.issubset(paths)


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
