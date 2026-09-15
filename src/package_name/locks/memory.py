"""In-process memory locks."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass


@dataclass
class _LockState:
    owner: str
    expires_at: float


class MemoryLockBackend:
    name = "memory"

    def __init__(self) -> None:
        self._locks: dict[str, _LockState] = {}
        self._guard = threading.RLock()

    def _purge_expired(self, key: str) -> None:
        state = self._locks.get(key)
        if state and state.expires_at <= time.time():
            del self._locks[key]

    def acquire(self, key: str, *, owner: str, ttl: float) -> bool:
        with self._guard:
            self._purge_expired(key)
            if key in self._locks:
                return False
            self._locks[key] = _LockState(owner=owner, expires_at=time.time() + ttl)
            return True

    def release(self, key: str, *, owner: str) -> bool:
        with self._guard:
            self._purge_expired(key)
            state = self._locks.get(key)
            if state is None or state.owner != owner:
                return False
            del self._locks[key]
            return True

    def refresh(self, key: str, *, owner: str, ttl: float) -> bool:
        with self._guard:
            self._purge_expired(key)
            state = self._locks.get(key)
            if state is None or state.owner != owner:
                return False
            state.expires_at = time.time() + ttl
            return True

    def owned_by(self, key: str, *, owner: str) -> bool:
        with self._guard:
            self._purge_expired(key)
            state = self._locks.get(key)
            return state is not None and state.owner == owner


def new_lock_owner() -> str:
    return str(uuid.uuid4())


__all__ = ["MemoryLockBackend", "new_lock_owner"]
