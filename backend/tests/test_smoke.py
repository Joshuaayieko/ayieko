"""Smoke tests: auth flow, chat (offline LLM), memory and tools."""

import os
import tempfile

# Use an isolated temp DB before importing the app.
os.environ.setdefault("ORBES_DATABASE_URL", f"sqlite:///{tempfile.mktemp(suffix='.db')}")
os.environ.setdefault("ORBES_ADMIN_EMAIL", "admin@test.dev")
os.environ.setdefault("ORBES_ADMIN_PASSWORD", "test-password")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    # Using TestClient as a context manager runs the app lifespan
    # (init_db + seed_admin) before tests execute.
    with TestClient(app) as c:
        yield c


def _login(client) -> str:
    resp = client.post(
        "/auth/login",
        data={"username": "admin@test.dev", "password": "test-password"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_root_and_health(client):
    assert client.get("/").json()["name"] == "Orbes"
    assert client.get("/health").json()["status"] == "healthy"


def test_admin_seeded_and_login(client):
    token = _login(client)
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "admin@test.dev"
    assert body["is_admin"] is True


def test_chat_offline(client):
    token = _login(client)
    resp = client.post(
        "/chat",
        json={"message": "Hello Orbes"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["conversation_id"]
    assert "reply" in data
    assert data["plan"]


def test_tool_intent_open_app(client):
    token = _login(client)
    resp = client.post(
        "/chat",
        json={"message": "open spotify"},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = resp.json()
    assert any(t["name"] == "open_app" for t in data["tools_used"])


def test_memory_crud(client):
    token = _login(client)
    h = {"Authorization": f"Bearer {token}"}
    created = client.post(
        "/memory", json={"key": "editor", "value": "dark mode"}, headers=h
    ).json()
    assert created["value"] == "dark mode"
    listed = client.get("/memory", headers=h).json()
    assert any(m["key"] == "editor" for m in listed)
    assert client.delete(f"/memory/{created['id']}", headers=h).status_code == 204
