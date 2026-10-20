import pytest

from meshvera.config import ConfigError, load_settings, load_settings_or_exit


def test_defaults_to_mock_mode() -> None:
    s = load_settings()
    assert s.llm_mode == "mock"
    assert s.app_env == "development"


def test_live_mode_requires_provider_model_and_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODE", "live")
    with pytest.raises(ConfigError) as exc:
        load_settings()
    msg = str(exc.value)
    assert "LLM_PROVIDER" in msg and "LLM_MODEL" in msg and "LLM_API_KEY" in msg


def test_live_mode_valid_and_secret_not_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODE", "live")
    monkeypatch.setenv("LLM_PROVIDER", "example")
    monkeypatch.setenv("LLM_MODEL", "m1")
    monkeypatch.setenv("LLM_API_KEY", "placeholder-secret-value")
    s = load_settings()
    assert s.llm_mode == "live"
    assert "placeholder-secret-value" not in repr(s)


def test_invalid_mode_rejected_not_coerced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODE", "auto")
    with pytest.raises(ConfigError):
        load_settings()


@pytest.mark.parametrize(
    ("name", "value"),
    [("API_PORT", "0"), ("MAX_NODES", "1"), ("MAX_ROUNDS", "0"), ("WORKER_POLL_SECONDS", "-1")],
)
def test_limits_validated(monkeypatch: pytest.MonkeyPatch, name: str, value: str) -> None:
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError):
        load_settings()


def test_bad_origin_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_ORIGIN", "localhost:8000")
    with pytest.raises(ConfigError):
        load_settings()


def test_entry_point_exits_2_on_bad_config(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LLM_MODE", "live")
    with pytest.raises(SystemExit) as exc:
        load_settings_or_exit()
    assert exc.value.code == 2
    assert "Invalid configuration" in capsys.readouterr().err
