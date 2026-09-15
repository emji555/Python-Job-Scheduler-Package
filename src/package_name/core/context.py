"""Job execution context via contextvars."""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class JobContext:
    id: str
    job: str
    attempt: int
    queue: str
    metadata: dict[str, Any] = field(default_factory=dict)
    max_attempts: int = 1


_current_job: ContextVar[JobContext | None] = ContextVar("package_name_current_job", default=None)


class _CurrentJobProxy:
    """Proxy so callers can use ``current_job.id`` style access."""

    def _get(self) -> JobContext:
        ctx = _current_job.get()
        if ctx is None:
            raise RuntimeError("No job is currently executing")
        return ctx

    @property
    def id(self) -> str:
        return self._get().id

    @property
    def job(self) -> str:
        return self._get().job

    @property
    def attempt(self) -> int:
        return self._get().attempt

    @property
    def queue(self) -> str:
        return self._get().queue

    @property
    def metadata(self) -> dict[str, Any]:
        return self._get().metadata

    @property
    def max_attempts(self) -> int:
        return self._get().max_attempts

    def __bool__(self) -> bool:
        return _current_job.get() is not None


current_job = _CurrentJobProxy()


def push_job_context(ctx: JobContext) -> Token[JobContext | None]:
    return _current_job.set(ctx)


def reset_job_context(token: Token[JobContext | None]) -> None:
    _current_job.reset(token)


def get_job_context() -> JobContext | None:
    return _current_job.get()


__all__ = [
    "JobContext",
    "current_job",
    "get_job_context",
    "push_job_context",
    "reset_job_context",
]
