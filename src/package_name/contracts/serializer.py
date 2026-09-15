"""Serializer protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Serializer(Protocol):
    name: str

    def dumps(self, value: Any) -> bytes:
        """Serialize a JSON-safe (or serializer-specific) value to bytes."""

    def loads(self, data: bytes) -> Any:
        """Deserialize bytes to a Python value."""


__all__ = ["Serializer"]
