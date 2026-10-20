import pytest

_ENV_NAMES = [
    "APP_ENV", "LLM_MODE", "LLM_PROVIDER", "LLM_MODEL", "LLM_API_KEY",
    "API_HOST", "API_PORT", "API_ORIGIN", "WORKER_POLL_SECONDS",
    "MAX_NODES", "MAX_ROUNDS", "MAX_TRIALS",
]  # fmt: skip


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> None:
    """Isolate tests from the developer's environment and any local .env file."""
    for name in _ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # no .env here
