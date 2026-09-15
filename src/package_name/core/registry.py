"""Job registry — only registered jobs may execute."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from package_name.core.retries import RetryPolicy
from package_name.exceptions import JobNotRegisteredError


@dataclass(slots=True)
class JobDefinition:
    name: str
    func: Callable[..., Any]
    queue: str = "default"
    retries: int = 0
    timeout: float | None = None
    backoff: str | int | float = 0
    jitter: bool = False
    max_delay: float | None = None
    retry_on: tuple[type[BaseException], ...] | None = None
    dont_retry_on: tuple[type[BaseException], ...] | None = None
    middleware: list[Any] = field(default_factory=list)
    idempotency_key: Callable[..., str] | str | None = None
    is_async: bool = False
    priority: str = "normal"

    @property
    def max_attempts(self) -> int:
        return max(self.retries, 0) + 1

    def retry_policy(self) -> RetryPolicy:
        return RetryPolicy(
            max_attempts=self.max_attempts,
            backoff=self.backoff,
            jitter=self.jitter,
            max_delay=self.max_delay,
            retry_on=self.retry_on,
            dont_retry_on=self.dont_retry_on,
        )


class JobRegistry:
    def __init__(self) -> None:
        self._jobs: dict[str, JobDefinition] = {}

    def register(self, definition: JobDefinition) -> JobDefinition:
        self._jobs[definition.name] = definition
        return definition

    def get(self, name: str) -> JobDefinition:
        try:
            return self._jobs[name]
        except KeyError as exc:
            raise JobNotRegisteredError(f"Job {name!r} is not registered") from exc

    def has(self, name: str) -> bool:
        return name in self._jobs

    def names(self) -> list[str]:
        return sorted(self._jobs)

    def all(self) -> list[JobDefinition]:
        return [self._jobs[name] for name in self.names()]

    def clear(self) -> None:
        self._jobs.clear()


def qualify_name(func: Callable[..., Any]) -> str:
    module = getattr(func, "__module__", "unknown")
    qual = getattr(func, "__qualname__", getattr(func, "__name__", "job"))
    return f"{module}.{qual}"


def detect_async(func: Callable[..., Any]) -> bool:
    return inspect.iscoroutinefunction(func)


__all__ = [
    "JobDefinition",
    "JobRegistry",
    "detect_async",
    "qualify_name",
]
