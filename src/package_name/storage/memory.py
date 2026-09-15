"""In-memory storage for failed jobs and idempotency."""

from __future__ import annotations

import threading
import time
from typing import Any

from package_name.core.failed import FailedJobRecord


class MemoryStorage:
    name = "memory"

    def __init__(self) -> None:
        self._failed: dict[str, FailedJobRecord] = {}
        self._idem: dict[str, tuple[dict[str, Any], float | None]] = {}
        self._lock = threading.RLock()

    def save_failed(self, record: FailedJobRecord) -> None:
        with self._lock:
            self._failed[record.id] = record

    def list_failed(self, *, limit: int = 100, offset: int = 0) -> list[FailedJobRecord]:
        with self._lock:
            items = sorted(self._failed.values(), key=lambda r: r.failed_at, reverse=True)
            return items[offset : offset + limit]

    def get_failed(self, failed_id: str) -> FailedJobRecord | None:
        with self._lock:
            return self._failed.get(failed_id)

    def delete_failed(self, failed_id: str) -> bool:
        with self._lock:
            return self._failed.pop(failed_id, None) is not None

    def clear_failed(self) -> int:
        with self._lock:
            count = len(self._failed)
            self._failed.clear()
            return count

    def get_idempotency(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._idem.get(key)
            if item is None:
                return None
            value, expires = item
            if expires is not None and time.time() > expires:
                del self._idem[key]
                return None
            return dict(value)

    def set_idempotency(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl: float | None = None,
    ) -> None:
        expires = time.time() + ttl if ttl is not None else None
        with self._lock:
            self._idem[key] = (dict(value), expires)


__all__ = ["MemoryStorage"]
