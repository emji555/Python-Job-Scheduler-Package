"""Plugin discovery via importlib.metadata entry points."""

from __future__ import annotations

import logging
from importlib.metadata import entry_points
from typing import Any, TypeVar

from workloom.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

T = TypeVar("T")

GROUP_BACKENDS = "workloom.backends"
GROUP_SCHEDULERS = "workloom.schedulers"
GROUP_SERIALIZERS = "workloom.serializers"
GROUP_STORAGE = "workloom.storage"
GROUP_LOCKS = "workloom.locks"
GROUP_MIDDLEWARE = "workloom.middleware"

# Fallbacks so editable/src layouts work before packaging entry points are visible.
_BUILTINS: dict[str, dict[str, str]] = {
    GROUP_BACKENDS: {
        "eager": "workloom.backends.eager:EagerBackend",
        "memory": "workloom.backends.memory:MemoryBackend",
        "celery": "workloom.backends.celery:CeleryBackend",
    },
    GROUP_SCHEDULERS: {
        "inprocess": "workloom.schedulers.inprocess:InProcessScheduler",
    },
    GROUP_SERIALIZERS: {
        "json": "workloom.serializers.json:JsonSerializer",
    },
    GROUP_STORAGE: {
        "memory": "workloom.storage.memory:MemoryStorage",
    },
    GROUP_LOCKS: {
        "memory": "workloom.locks.memory:MemoryLockBackend",
        "redis": "workloom.locks.redis:RedisLockBackend",
    },
}


def _select(group: str) -> Any:
    eps = entry_points()
    if hasattr(eps, "select"):
        return eps.select(group=group)
    return eps.get(group, [])  # type: ignore[attr-defined]


def _load_dotted(path: str) -> Any:
    module_name, _, attr = path.partition(":")
    if not module_name or not attr:
        raise ConfigurationError(f"Invalid plugin path {path!r}")
    import importlib

    module = importlib.import_module(module_name)
    return getattr(module, attr)


def list_plugins(group: str) -> dict[str, Any]:
    """Return mapping of plugin name -> entry point object or dotted path."""
    found: dict[str, Any] = {ep.name: ep for ep in _select(group)}
    for name, dotted in _BUILTINS.get(group, {}).items():
        found.setdefault(name, dotted)
    return found


def load_plugin(group: str, name: str) -> Any:
    """Load a plugin class/factory by group and name."""
    plugins = list_plugins(group)
    if name not in plugins:
        available = ", ".join(sorted(plugins)) or "(none)"
        raise ConfigurationError(
            f"Unknown plugin {name!r} in group {group!r}. Available: {available}"
        )
    ep = plugins[name]
    logger.debug("Loading plugin %s:%s", group, name)
    if isinstance(ep, str):
        return _load_dotted(ep)
    return ep.load()


__all__ = [
    "GROUP_BACKENDS",
    "GROUP_LOCKS",
    "GROUP_MIDDLEWARE",
    "GROUP_SCHEDULERS",
    "GROUP_SERIALIZERS",
    "GROUP_STORAGE",
    "list_plugins",
    "load_plugin",
]
