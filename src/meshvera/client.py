"""Small API client used by the Streamlit shell (kept out of ui/ so it is testable)."""

from __future__ import annotations

from typing import Any

import httpx


def fetch_health(
    api_origin: str,
    transport: httpx.BaseTransport | None = None,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Return {'ok': bool, 'data' | 'error': ...}; never raises on connection problems."""
    try:
        with httpx.Client(base_url=api_origin, timeout=timeout, transport=transport) as client:
            resp = client.get("/health")
            resp.raise_for_status()
            return {"ok": True, "data": resp.json()}
    except (httpx.HTTPError, ValueError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
