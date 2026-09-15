"""Redis distributed locks with safe owner-token release."""

from __future__ import annotations

from typing import Any

from workloom.exceptions import ConfigurationError, LockError

# Release only if token matches
_RELEASE_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('del', KEYS[1])
else
  return 0
end
"""

_REFRESH_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
  return redis.call('pexpire', KEYS[1], ARGV[2])
else
  return 0
end
"""


class RedisLockBackend:
    name = "redis"

    def __init__(self, url: str | None = None, client: Any | None = None) -> None:
        if client is not None:
            self._client = client
        else:
            try:
                import redis
            except ImportError as exc:
                raise ConfigurationError(
                    "RedisLockBackend requires the 'redis' extra: pip install 'workloom[redis]'"
                ) from exc
            if not url:
                raise ConfigurationError("RedisLockBackend requires a broker/redis URL")
            self._client = redis.Redis.from_url(url, decode_responses=True)

    def acquire(self, key: str, *, owner: str, ttl: float) -> bool:
        try:
            return bool(self._client.set(key, owner, nx=True, px=int(ttl * 1000)))
        except Exception as exc:
            raise LockError(f"Failed to acquire lock {key!r}: {exc}") from exc

    def release(self, key: str, *, owner: str) -> bool:
        try:
            result = self._client.eval(_RELEASE_LUA, 1, key, owner)
            return bool(result)
        except Exception as exc:
            raise LockError(f"Failed to release lock {key!r}: {exc}") from exc

    def refresh(self, key: str, *, owner: str, ttl: float) -> bool:
        try:
            result = self._client.eval(_REFRESH_LUA, 1, key, owner, str(int(ttl * 1000)))
            return bool(result)
        except Exception as exc:
            raise LockError(f"Failed to refresh lock {key!r}: {exc}") from exc

    def owned_by(self, key: str, *, owner: str) -> bool:
        try:
            return self._client.get(key) == owner
        except Exception as exc:
            raise LockError(f"Failed to inspect lock {key!r}: {exc}") from exc


__all__ = ["RedisLockBackend"]
