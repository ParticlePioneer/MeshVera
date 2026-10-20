import threading

import httpx
import pytest

from meshvera.client import fetch_health
from meshvera.config import load_settings
from meshvera.worker.main import main, run_worker


def test_run_worker_stops_after_max_polls() -> None:
    assert run_worker(load_settings(), threading.Event(), max_polls=1) == 1


def test_run_worker_respects_stop_event() -> None:
    stop = threading.Event()
    stop.set()
    assert run_worker(load_settings(), stop) == 0


def test_worker_main_once_exits_zero() -> None:
    assert main(["--once"]) == 0


def test_worker_main_fails_fast_on_bad_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_MODE", "live")
    with pytest.raises(SystemExit) as exc:
        main(["--once"])
    assert exc.value.code == 2


def test_fetch_health_ok() -> None:
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={"status": "ok"}))
    result = fetch_health("http://test", transport=transport)
    assert result == {"ok": True, "data": {"status": "ok"}}


def test_fetch_health_reports_unreachable_without_raising() -> None:
    def boom(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    result = fetch_health("http://test", transport=httpx.MockTransport(boom))
    assert result["ok"] is False
    assert "ConnectError" in result["error"]
