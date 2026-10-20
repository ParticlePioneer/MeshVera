"""Strict, fail-fast application settings.

LLM mode is explicit: ``mock`` (default, no network) or ``live``.
A failed or incomplete live configuration is an error; it never degrades to mock.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True
    )

    app_env: Literal["development", "test", "production"] = "development"

    llm_mode: Literal["mock", "live"] = "mock"
    llm_provider: str = ""
    llm_model: str = ""
    llm_api_key: SecretStr = SecretStr("")

    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_origin: str = "http://127.0.0.1:8000"

    worker_poll_seconds: float = Field(default=2.0, gt=0, le=300)

    max_nodes: int = Field(default=50, ge=2, le=1000)
    max_rounds: int = Field(default=200, ge=1, le=10000)
    max_trials: int = Field(default=20, ge=1, le=1000)

    @model_validator(mode="after")
    def _check_live_mode(self) -> Settings:
        if self.llm_mode == "live":
            missing = [
                name
                for name, value in (
                    ("LLM_PROVIDER", self.llm_provider.strip()),
                    ("LLM_MODEL", self.llm_model.strip()),
                    ("LLM_API_KEY", self.llm_api_key.get_secret_value().strip()),
                )
                if not value
            ]
            if missing:
                raise ValueError(
                    "LLM_MODE=live requires " + ", ".join(missing) + " (or set LLM_MODE=mock)"
                )
        return self

    @model_validator(mode="after")
    def _check_origin(self) -> Settings:
        if not self.api_origin.startswith(("http://", "https://")):
            raise ValueError("API_ORIGIN must start with http:// or https://")
        return self


class ConfigError(RuntimeError):
    """Raised with a readable message when settings are invalid."""


def load_settings() -> Settings:
    """Build settings from the environment, raising ConfigError on invalid values."""
    try:
        return Settings()
    except ValidationError as exc:
        lines = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"]).upper() or "settings"
            lines.append(f"  - {loc}: {err['msg']}")
        raise ConfigError("Invalid configuration:\n" + "\n".join(lines)) from None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return load_settings()


def load_settings_or_exit() -> Settings:
    """For entry points: print a clear message and exit with code 2 on bad config."""
    try:
        return load_settings()
    except ConfigError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(2) from None
