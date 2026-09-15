"""Backend capability flags and job backend protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from package_name.core.envelope import JobEnvelope
    from package_name.core.result import JobHandle, JobStatus


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    delayed_jobs: bool = False
    results: bool = False
    cancellation: bool = False
    priority: bool = False
    distributed_locks: bool = False
    monitoring: bool = False
    retries: bool = True
    async_jobs: bool = False
    chains: bool = False
    groups: bool = False

    def require(self, name: str) -> None:
        from package_name.exceptions import UnsupportedCapabilityError

        if not getattr(self, name, False):
            raise UnsupportedCapabilityError(f"Backend does not support capability {name!r}")


@runtime_checkable
class JobBackend(Protocol):
    """Protocol for queue/job execution backends."""

    name: str
    capabilities: BackendCapabilities

    def dispatch(self, envelope: JobEnvelope) -> JobHandle:
        """Enqueue or execute a job envelope; return a handle."""

    def get_status(self, job_id: str) -> JobStatus:
        """Return current status for a job id."""

    def get_result(self, job_id: str, *, timeout: float | None = None) -> Any:
        """Return job result if supported."""

    def cancel(self, job_id: str) -> bool:
        """Attempt cancellation if supported. Return True if cancelled."""

    def purge(self, queue: str | None = None) -> int:
        """Optional: remove pending jobs. Return count removed."""

    def queue_depth(self, queue: str | None = None) -> int | None:
        """Optional monitoring helper."""


__all__ = ["BackendCapabilities", "JobBackend"]
