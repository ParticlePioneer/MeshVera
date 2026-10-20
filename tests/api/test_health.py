from fastapi.testclient import TestClient

from meshvera.api.main import create_app
from meshvera.config import Settings


def test_health_ok_in_default_mock_mode() -> None:
    client = TestClient(create_app(Settings()))
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["llm_mode"] == "mock"


def test_health_never_leaks_secret() -> None:
    s = Settings(
        llm_mode="live", llm_provider="p", llm_model="m", llm_api_key="placeholder-secret-value"
    )
    resp = TestClient(create_app(s)).get("/health")
    assert "placeholder-secret-value" not in resp.text
    assert resp.json()["llm_mode"] == "live"
