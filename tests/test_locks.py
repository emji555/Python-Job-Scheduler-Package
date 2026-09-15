"""Lock backend tests."""

from __future__ import annotations

from package_name.locks.memory import MemoryLockBackend


def test_memory_lock_owner_protection() -> None:
    locks = MemoryLockBackend()
    assert locks.acquire("k", owner="a", ttl=30) is True
    assert locks.acquire("k", owner="b", ttl=30) is False
    assert locks.release("k", owner="b") is False
    assert locks.refresh("k", owner="a", ttl=30) is True
    assert locks.release("k", owner="a") is True
    assert locks.acquire("k", owner="b", ttl=30) is True
