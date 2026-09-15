"""Configuration objects and environment loading."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from typing import Any

from workloom.exceptions import ConfigurationError

ENV_PREFIX = "WORKLOOM_"


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable configuration snapshot.

    Precedence when building via :func:`load_settings`:
    1. Explicit keyword overrides
    2. Environment variables (`WORKLOOM_*`)
    3. Defaults below
    """

    backend: str = "eager"
    broker_url: str | None = None
    result_backend: str | None = None
    default_queue: str = "default"
    timezone: str = "UTC"
    serializer: str = "json"
    storage: str = "memory"
    lock_backend: str = "memory"
    scheduler: str = "inprocess"
    max_attempts: int = 1
    default_timeout: float | None = None
    redact_keys: tuple[str, ...] = (
        "password",
        "secret",
        "token",
        "api_key",
        "authorization",
        "access_token",
        "refresh_token",
    )
    extra: dict[str, Any] = field(default_factory=dict)

    def with_overrides(self, **kwargs: Any) -> Settings:
        return replace(self, **kwargs)


def _env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(f"{ENV_PREFIX}{name}", default)


def load_settings(**overrides: Any) -> Settings:
    """Load settings from environment then apply explicit overrides."""
    backend = _env("BACKEND", "eager") or "eager"
    broker_url = _env("BROKER_URL")
    result_backend = _env("RESULT_BACKEND")
    default_queue = _env("DEFAULT_QUEUE", "default") or "default"
    timezone = _env("TIMEZONE", "UTC") or "UTC"
    serializer = _env("SERIALIZER", "json") or "json"
    storage = _env("STORAGE", "memory") or "memory"
    lock_backend = _env("LOCK_BACKEND", "memory") or "memory"
    scheduler = _env("SCHEDULER", "inprocess") or "inprocess"

    max_attempts_raw = _env("MAX_ATTEMPTS", "1") or "1"
    try:
        max_attempts = int(max_attempts_raw)
    except ValueError as exc:
        raise ConfigurationError(f"Invalid {ENV_PREFIX}MAX_ATTEMPTS={max_attempts_raw!r}") from exc

    timeout_raw = _env("DEFAULT_TIMEOUT")
    default_timeout: float | None
    if timeout_raw is None or timeout_raw == "":
        default_timeout = None
    else:
        try:
            default_timeout = float(timeout_raw)
        except ValueError as exc:
            raise ConfigurationError(
                f"Invalid {ENV_PREFIX}DEFAULT_TIMEOUT={timeout_raw!r}"
            ) from exc

    base = Settings(
        backend=backend,
        broker_url=broker_url,
        result_backend=result_backend,
        default_queue=default_queue,
        timezone=timezone,
        serializer=serializer,
        storage=storage,
        lock_backend=lock_backend,
        scheduler=scheduler,
        max_attempts=max_attempts,
        default_timeout=default_timeout,
    )
    if overrides:
        # Filter unknown keys into extra
        known = {f.name for f in Settings.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        known_overrides = {k: v for k, v in overrides.items() if k in known and k != "extra"}
        extra = dict(base.extra)
        extra.update({k: v for k, v in overrides.items() if k not in known})
        if "extra" in overrides and isinstance(overrides["extra"], dict):
            extra.update(overrides["extra"])
        return base.with_overrides(**known_overrides, extra=extra)
    return base


__all__ = ["ENV_PREFIX", "Settings", "load_settings"]
