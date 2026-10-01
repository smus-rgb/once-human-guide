import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

import api_main
import install
import updater


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "once_human.db"
    assert install.rebuild_sqlite(Path(__file__).parent / "database_full.json", db) == 372
    monkeypatch.setattr(api_main, "DB_PATH", db)
    return TestClient(api_main.app)


def test_ui_assets_load(client):
    html = client.get("/ui")
    assert html.status_code == 200
    assert "modules/ohg_runtime.js" in html.text
    for asset in (
        "once_human_guide_v19.html", "once_human_guide_v18.html",
        "ohg_data.js", "ohg_sw.js", "version.json",
        "modules/ohg_runtime.js", "modules/ohg_map.js",
        "modules/ohg_builds.js", "modules/ohg_pack_channel.js",
    ):
        response = client.get("/" + asset)
        assert response.status_code == 200, asset
        assert response.content, asset
    assert client.get("/modules/missing.js").status_code == 404
    assert client.get("/modules/..%2Fapi_main.py").status_code == 404


def test_search_and_edge_cases(client):
    result = client.get("/search", params={"q": "Butterfly"})
    assert result.status_code == 200
    assert any(x["id"] == "dev_butterfly" for x in result.json()["results"])
    assert client.get("/search", params={"q": ""}).status_code == 422
    assert client.get("/search", params={"q": "Butterfly", "limit": 1}).json()["count"] == 1
    assert client.get("/stats").json()["total"] == 372


def test_update_check(client, monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            return (Path(__file__).parent / "version.json").read_bytes()

    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: Response())
    result = client.get("/update/check")
    assert result.status_code == 200
    assert result.json()["ok"] is True
    assert result.json()["update_available"] is False
    assert result.json()["shell"]["host"] == "once_human_guide_v19.html"


def test_json_modules_build_without_duplicate_ids(tmp_path):
    modules = {}
    ids = set()
    for table, filename in updater.MODULE_FILES:
        rows = json.loads((Path(__file__).parent / filename).read_text())
        assert isinstance(rows, list)
        for row in rows:
            assert row["id"] and row["name"]
            assert row["id"] not in ids
            ids.add(row["id"])
        modules[table] = rows
        (tmp_path / filename).write_text(json.dumps(rows))
    (tmp_path / "version.json").write_text((Path(__file__).parent / "version.json").read_text())
    rebuilt = updater.assemble_database_full(tmp_path)
    assert rebuilt is not None
    assert sum(map(len, modules.values())) == 372
    assert updater.rebuild_sqlite(rebuilt, tmp_path / "once_human.db") == 372


def test_update_run_requires_configured_token(client, monkeypatch):
    import subprocess

    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append(args))
    monkeypatch.delenv("OHG_ADMIN_TOKEN", raising=False)
    assert client.post("/update/run").status_code == 403
    assert client.post("/update/run", headers={"X-OHG-Admin-Token": "unconfigured"}).status_code == 403
    monkeypatch.setenv("OHG_ADMIN_TOKEN", "")
    assert client.post("/update/run", headers={"X-OHG-Admin-Token": "unconfigured"}).status_code == 403
    assert not calls


def test_update_run_rejects_missing_or_wrong_token(client, monkeypatch):
    import secrets
    import subprocess

    token = secrets.token_urlsafe(24)
    monkeypatch.setenv("OHG_ADMIN_TOKEN", token)
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append(args))
    assert client.post("/update/run").status_code == 403
    assert client.post("/update/run?force=true", headers={"X-OHG-Admin-Token": "not-" + token}).status_code == 403
    assert not calls


def test_update_run_authorized_and_force(client, monkeypatch):
    import secrets
    import subprocess

    token = secrets.token_urlsafe(24)
    monkeypatch.setenv("OHG_ADMIN_TOKEN", token)
    commands = []

    def fake_run(cmd, **kwargs):
        commands.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, 0, stdout="updated", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    headers = {"X-OHG-Admin-Token": token}
    for url, force in (("/update/run", False), ("/update/run?force=true", True)):
        response = client.post(url, headers=headers)
        assert response.status_code == 200
        assert response.json()["ok"] is True
        assert response.json()["stdout"] == "updated"
        assert ("--force" in commands[-1][0]) is force
    assert all(kwargs["timeout"] == 180 for _, kwargs in commands)


def test_update_run_timeout(client, monkeypatch):
    import secrets
    import subprocess

    token = secrets.token_urlsafe(24)
    monkeypatch.setenv("OHG_ADMIN_TOKEN", token)

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert client.post("/update/run", headers={"X-OHG-Admin-Token": token}).status_code == 504


def test_launchers_bind_to_loopback(tmp_path):
    install.write_launchers(tmp_path)
    assert "--host 127.0.0.1" in (tmp_path / "start.sh").read_text()
    root = Path(__file__).parent
    for filename in ("start.sh", "install.py", "install_gui.py", "api_main.py"):
        source = (root / filename).read_text()
        assert "0.0.0.0" not in source
        assert "127.0.0.1" in source
