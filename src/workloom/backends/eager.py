"""Eager backend — execute immediately in the calling process."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from workloom.contracts.backend import BackendCapabilities
from workloom.core.envelope import JobEnvelope
from workloom.core.executor import execute_envelope
from workloom.core.result import JobHandle, JobStatus
from workloom.exceptions import UnsupportedCapabilityError

if TYPE_CHECKING:
    from workloom.app import App


class EagerBackend:
    """Excellent for tests, scripts, and local development."""

    name = "eager"
    capabilities = BackendCapabilities(
        delayed_jobs=False,
        results=True,
        cancellation=False,
        priority=False,
        distributed_locks=False,
        monitoring=False,
        retries=True,
        async_jobs=True,
        chains=True,
        groups=True,
    )

    def __init__(self, app: App | None = None) -> None:
        self._app = app
        self._results: dict[str, Any] = {}
        self._status: dict[str, JobStatus] = {}

    def bind(self, app: App) -> EagerBackend:
        self._app = app
        return self

    def dispatch(self, envelope: JobEnvelope) -> JobHandle:
        if self._app is None:
            raise RuntimeError("EagerBackend is not bound to an App")
        if envelope.run_at is not None:
            self.capabilities.require("delayed_jobs")
        self._status[envelope.id] = JobStatus.RUNNING
        try:
            result = execute_envelope(self._app, envelope)
            self._results[envelope.id] = result
            self._status[envelope.id] = JobStatus.SUCCEEDED
        except Exception:
            self._status[envelope.id] = JobStatus.FAILED
            raise
        return JobHandle(id=envelope.id, _backend=self, _app=self._app)

    def get_status(self, job_id: str) -> JobStatus:
        return self._status.get(job_id, JobStatus.UNKNOWN)

    def get_result(self, job_id: str, *, timeout: float | None = None) -> Any:
        _ = timeout
        if job_id not in self._results:
            raise KeyError(job_id)
        return self._results[job_id]

    def cancel(self, job_id: str) -> bool:
        raise UnsupportedCapabilityError("EagerBackend does not support cancellation")

    def purge(self, queue: str | None = None) -> int:
        _ = queue
        return 0

    def queue_depth(self, queue: str | None = None) -> int | None:
        _ = queue
        return 0


# Back-compat alias referenced temporarily in jobs.py (removed usage preferred)
EagerHandle = JobHandle

__all__ = ["EagerBackend", "EagerHandle"]
