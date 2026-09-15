"""Lock backend protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LockBackend(Protocol):
    name: str

    def acquire(self, key: str, *, owner: str, ttl: float) -> bool:
        """Acquire a lock. Return True if acquired."""

    def release(self, key: str, *, owner: str) -> bool:
        """Release only if owner matches. Return True if released."""

    def refresh(self, key: str, *, owner: str, ttl: float) -> bool:
        """Refresh TTL if owner matches."""

    def owned_by(self, key: str, *, owner: str) -> bool:
        """Return True if the lock exists and is owned by owner."""


__all__ = ["LockBackend"]
