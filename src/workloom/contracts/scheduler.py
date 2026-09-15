"""Scheduler backend protocol."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from workloom.schedulers.core import ScheduledEvent, ScheduleEntry


@runtime_checkable
class SchedulerBackend(Protocol):
    name: str

    def add(self, entry: ScheduleEntry) -> None: ...

    def remove(self, entry_id: str) -> bool: ...

    def list(self) -> builtins.list[ScheduleEntry]: ...

    def tick(self) -> builtins.list[ScheduledEvent]:
        """Advance scheduler clock and return due events (for poll-based backends)."""

    def start(self) -> None: ...

    def stop(self) -> None: ...


__all__ = ["SchedulerBackend"]
