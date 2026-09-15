"""Payload and metadata redaction helpers."""

from __future__ import annotations

from typing import Any


def _should_redact(key: str, redact_keys: tuple[str, ...]) -> bool:
    lowered = key.lower()
    return any(token.lower() in lowered for token in redact_keys)


def redact_mapping(value: Any, redact_keys: tuple[str, ...]) -> Any:
    """Recursively redact sensitive keys in mappings/lists."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if _should_redact(str(key), redact_keys):
                out[str(key)] = "***REDACTED***"
            else:
                out[str(key)] = redact_mapping(item, redact_keys)
        return out
    if isinstance(value, list):
        return [redact_mapping(item, redact_keys) for item in value]
    return value


__all__ = ["redact_mapping"]
