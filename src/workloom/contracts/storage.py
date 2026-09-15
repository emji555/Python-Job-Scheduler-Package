"""Storage backend protocol for failed jobs and idempotency."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from workloom.core.failed import FailedJobRecord


@runtime_checkable
class StorageBackend(Protocol):
    name: str

    def save_failed(self, record: FailedJobRecord) -> None: ...

    def list_failed(self, *, limit: int = 100, offset: int = 0) -> list[FailedJobRecord]: ...

    def get_failed(self, failed_id: str) -> FailedJobRecord | None: ...

    def delete_failed(self, failed_id: str) -> bool: ...

    def clear_failed(self) -> int: ...

    def get_idempotency(self, key: str) -> dict[str, Any] | None: ...

    def set_idempotency(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl: float | None = None,
    ) -> None: ...


__all__ = ["StorageBackend"]
