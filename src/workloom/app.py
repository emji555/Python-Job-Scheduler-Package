"""Application container and default-app helpers."""

from __future__ import annotations

import logging
import threading
from typing import Any

from workloom.config import Settings, load_settings
from workloom.contracts.backend import JobBackend
from workloom.contracts.locks import LockBackend
from workloom.contracts.scheduler import SchedulerBackend
from workloom.contracts.serializer import Serializer
from workloom.contracts.storage import StorageBackend
from workloom.core.events import EventBus
from workloom.core.failed import FailedJobs
from workloom.core.middleware import Middleware, MiddlewareStack
from workloom.core.registry import JobRegistry
from workloom.monitoring.api import MonitorAPI
from workloom.plugins import (
    GROUP_BACKENDS,
    GROUP_LOCKS,
    GROUP_SCHEDULERS,
    GROUP_SERIALIZERS,
    GROUP_STORAGE,
    load_plugin,
)
from workloom.schedulers.core import Schedule

logger = logging.getLogger(__name__)

_default_app_lock = threading.RLock()
_default_app: App | None = None


class App:
    """Explicit application instance — preferred for tests and multi-app processes."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        backend: JobBackend | str | None = None,
        storage: StorageBackend | str | None = None,
        serializer: Serializer | str | None = None,
        lock_backend: LockBackend | str | None = None,
        scheduler: SchedulerBackend | str | None = None,
        middleware: list[Middleware] | None = None,
        **config_overrides: Any,
    ) -> None:
        self.settings = settings or load_settings(**config_overrides)
        if config_overrides and settings is not None:
            self.settings = self.settings.with_overrides(
                **{k: v for k, v in config_overrides.items() if hasattr(self.settings, k)}
            )

        self.registry = JobRegistry()
        self.events = EventBus()
        self.middleware_stack = MiddlewareStack(middleware)
        self._stats = {
            "dispatched": 0,
            "succeeded": 0,
            "failed": 0,
            "retried": 0,
        }
        self._stats_lock = threading.RLock()

        self.serializer = self._resolve_serializer(serializer)
        self.storage = self._resolve_storage(storage)
        self.lock_backend = self._resolve_lock(lock_backend)
        self.backend = self._resolve_backend(backend)
        self.scheduler_backend = self._resolve_scheduler(scheduler)
        self.schedule = Schedule(self)
        self.failed_jobs = FailedJobs(self)
        self.monitor = MonitorAPI(self)

    def _resolve_serializer(self, value: Serializer | str | None) -> Serializer:
        if value is None:
            value = self.settings.serializer
        if isinstance(value, str):
            cls = load_plugin(GROUP_SERIALIZERS, value)
            return cls()  # type: ignore[no-any-return]
        return value

    def _resolve_storage(self, value: StorageBackend | str | None) -> StorageBackend:
        if value is None:
            value = self.settings.storage
        if isinstance(value, str):
            cls = load_plugin(GROUP_STORAGE, value)
            return cls()  # type: ignore[no-any-return]
        return value

    def _resolve_lock(self, value: LockBackend | str | None) -> LockBackend:
        if value is None:
            value = self.settings.lock_backend
        if isinstance(value, str):
            cls = load_plugin(GROUP_LOCKS, value)
            if value == "redis":
                return cls(url=self.settings.broker_url)  # type: ignore[no-any-return]
            return cls()  # type: ignore[no-any-return]
        return value

    def _resolve_backend(self, value: JobBackend | str | None) -> JobBackend:
        if value is None:
            value = self.settings.backend
        if isinstance(value, str):
            cls = load_plugin(GROUP_BACKENDS, value)
            if value == "celery":
                instance = cls(
                    self,
                    broker_url=self.settings.broker_url,
                    result_backend=self.settings.result_backend,
                )
            else:
                instance = cls(self)
            if hasattr(instance, "bind"):
                instance.bind(self)
            return instance  # type: ignore[no-any-return]
        if hasattr(value, "bind"):
            value.bind(self)  # type: ignore[attr-defined]
        return value

    def _resolve_scheduler(self, value: SchedulerBackend | str | None) -> SchedulerBackend:
        if value is None:
            value = self.settings.scheduler
        if isinstance(value, str):
            cls = load_plugin(GROUP_SCHEDULERS, value)
            instance = cls(self)
            if hasattr(instance, "bind"):
                instance.bind(self)
            return instance  # type: ignore[no-any-return]
        if hasattr(value, "bind"):
            value.bind(self)  # type: ignore[attr-defined]
        return value

    def record_dispatch(self) -> None:
        with self._stats_lock:
            self._stats["dispatched"] += 1

    def record_success(self) -> None:
        with self._stats_lock:
            self._stats["succeeded"] += 1

    def record_failure(self) -> None:
        with self._stats_lock:
            self._stats["failed"] += 1

    def record_retry(self) -> None:
        with self._stats_lock:
            self._stats["retried"] += 1

    def stats(self) -> dict[str, int]:
        with self._stats_lock:
            return dict(self._stats)

    def use(self) -> App:
        """Set this app as the process default."""
        set_current_app(self)
        return self


def get_current_app() -> App:
    global _default_app
    with _default_app_lock:
        if _default_app is None:
            _default_app = App()
        return _default_app


def set_current_app(app: App | None) -> None:
    global _default_app
    with _default_app_lock:
        _default_app = app


def configure(**kwargs: Any) -> App:
    """Configure (and replace) the default application."""
    app = App(**kwargs)
    set_current_app(app)
    return app


def reset_default_app() -> None:
    """Reset default app — primarily for tests."""
    set_current_app(None)


__all__ = [
    "App",
    "configure",
    "get_current_app",
    "reset_default_app",
    "set_current_app",
]
