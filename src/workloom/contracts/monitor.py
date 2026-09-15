"""Monitoring protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Monitor(Protocol):
    def queues(self) -> list[dict[str, Any]]: ...

    def workers(self) -> list[dict[str, Any]]: ...

    def failed_jobs(self) -> list[dict[str, Any]]: ...

    def stats(self) -> dict[str, Any]: ...


__all__ = ["Monitor"]
