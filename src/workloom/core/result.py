"""Job status and dispatch handles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from workloom.app import App
    from workloom.contracts.backend import JobBackend


class JobStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class JobHandle:
    """Opaque handle returned by every dispatch."""

    id: str
    _backend: JobBackend
    _app: App | None = None

    def status(self) -> JobStatus:
        return self._backend.get_status(self.id)

    def result(self, *, timeout: float | None = None) -> Any:
        self._backend.capabilities.require("results")
        return self._backend.get_result(self.id, timeout=timeout)

    def cancel(self) -> bool:
        self._backend.capabilities.require("cancellation")
        return self._backend.cancel(self.id)


__all__ = ["JobHandle", "JobStatus"]
