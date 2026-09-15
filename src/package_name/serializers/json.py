"""JSON serializer (default, safe)."""

from __future__ import annotations

import json
from typing import Any

from package_name.exceptions import SerializationError


class JsonSerializer:
    name = "json"

    def dumps(self, value: Any) -> bytes:
        try:
            return json.dumps(value, default=self._default, separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise SerializationError(f"Value is not JSON-serializable: {exc}") from exc

    def loads(self, data: bytes) -> Any:
        try:
            return json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SerializationError(f"Invalid JSON payload: {exc}") from exc

    @staticmethod
    def _default(obj: Any) -> Any:
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


__all__ = ["JsonSerializer"]
