"""Generic monitoring API (Horizon-ready interfaces, no Django Admin)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from package_name.app import App


class MonitorAPI:
    def __init__(self, app: App) -> None:
        self._app = app

    def queues(self) -> list[dict[str, Any]]:
        depth = self._app.backend.queue_depth()
        return [
            {
                "name": self._app.settings.default_queue,
                "depth": depth,
            }
        ]

    def workers(self) -> list[dict[str, Any]]:
        # Process-local backends do not expose remote workers in 0.1
        return []

    def failed_jobs(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self._app.failed_jobs.list()]

    def stats(self) -> dict[str, Any]:
        return {
            **self._app.stats(),
            "registered_jobs": self._app.registry.names(),
            "backend": getattr(self._app.backend, "name", type(self._app.backend).__name__),
            "capabilities": {
                field: getattr(self._app.backend.capabilities, field)
                for field in self._app.backend.capabilities.__dataclass_fields__  # type: ignore[attr-defined]
            },
        }


__all__ = ["MonitorAPI"]
