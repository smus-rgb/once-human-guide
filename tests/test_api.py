"""Smoke tests for the Once Human Guide API and database builder.

Keeps the GitHub Actions "build" job (flake8 + pytest) meaningful without a
live server or a pre-built SQLite file.
"""
from __future__ import annotations

import sqlite3

import api_main
import db_build


def test_api_routes_registered():
    paths = {route.path for route in api_main.app.routes}
    assert {"/", "/health", "/ui", "/stats", "/search"}.issubset(paths)


def test_api_versions_loaded():
    assert api_main.API_VERSION
    assert api_main.DATA_VERSION


def test_fts_query_is_sanitized():
    assert api_main._fts_query("soc r?!") == "soc* r*"


def test_db_build_creates_core_tables(tmp_path):
    db_path = tmp_path / "once_human.db"
    result = db_build.build(db_path)
    assert result["records"] > 0

    conn = sqlite3.connect(db_path)
    try:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    finally:
        conn.close()
    assert {
        "deviations",
        "weapons",
        "entities",
        "entities_fts",
        "links",
        "data_issues",
    }.issubset(names)
