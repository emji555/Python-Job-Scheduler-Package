"""Lifecycle events and in-process event bus."""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

Listener = Callable[[Any], None]


@dataclass(slots=True)
class JobDispatched:
    job_id: str
    job: str
    queue: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class JobStarted:
    job_id: str
    job: str
    attempt: int


@dataclass(slots=True)
class JobSucceeded:
    job_id: str
    job: str
    result: Any = None


@dataclass(slots=True)
class JobFailed:
    job_id: str
    job: str
    exception: BaseException
    attempt: int


@dataclass(slots=True)
class JobRetrying:
    job_id: str
    job: str
    attempt: int
    delay: float
    exception: BaseException


@dataclass(slots=True)
class JobCancelled:
    job_id: str
    job: str


class EventBus:
    """Simple in-process event bus. Not a distributed pub/sub."""

    def __init__(self) -> None:
        self._listeners: dict[type[Any], list[Listener]] = defaultdict(list)

    def on(self, event_type: type[Any], listener: Listener) -> None:
        self._listeners[event_type].append(listener)

    def off(self, event_type: type[Any], listener: Listener) -> None:
        if listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def emit(self, event: Any) -> None:
        for listener in list(self._listeners.get(type(event), [])):
            try:
                listener(event)
            except Exception:
                logger.exception("Event listener failed for %s", type(event).__name__)


__all__ = [
    "EventBus",
    "JobCancelled",
    "JobDispatched",
    "JobFailed",
    "JobRetrying",
    "JobStarted",
    "JobSucceeded",
    "Listener",
]
