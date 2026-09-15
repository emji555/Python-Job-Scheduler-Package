"""Laravel-inspired fluent schedule declarations."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from croniter import croniter

from package_name.core.jobs import Job
from package_name.exceptions import SchedulerError
from package_name.locks.memory import new_lock_owner

if TYPE_CHECKING:
    from package_name.app import App


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


@dataclass(slots=True)
class ScheduleEntry:
    id: str
    job_name: str
    cron: str
    timezone: str = "UTC"
    without_overlapping: bool = False
    on_one_server: bool = False
    overlap_ttl: float = 3600.0
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    last_run_at: datetime | None = None
    description: str = ""

    def next_run_after(self, moment: datetime) -> datetime:
        tz = ZoneInfo(self.timezone)
        local = moment.astimezone(tz)
        itr = croniter(self.cron, local)
        nxt = itr.get_next(datetime)
        if nxt.tzinfo is None:
            nxt = nxt.replace(tzinfo=tz)
        return nxt.astimezone(timezone.utc)


@dataclass(slots=True)
class ScheduledEvent:
    entry: ScheduleEntry
    due_at: datetime


class ScheduledJob:
    """Fluent builder for a single scheduled job."""

    def __init__(self, schedule: Schedule, job: Job[Any, Any] | Callable[..., Any]) -> None:
        self._schedule = schedule
        self._job: Job[Any, Any] | Callable[..., Any]
        if isinstance(job, Job):
            self._job_name = job.name
            self._job = job
        else:
            from package_name.core.registry import qualify_name

            self._job_name = qualify_name(job)
            self._job = job
        self._cron: str | None = None
        self._timezone = schedule.app.settings.timezone
        self._without_overlapping = False
        self._on_one_server = False
        self._overlap_ttl = 3600.0
        self._args: tuple[Any, ...] = ()
        self._kwargs: dict[str, Any] = {}
        self._entry_id = str(uuid.uuid4())

    def timezone(self, name: str) -> ScheduledJob:
        self._timezone = name
        return self._recommit()

    def every_minute(self) -> ScheduledJob:
        self._cron = "* * * * *"
        return self._commit()

    def every_five_minutes(self) -> ScheduledJob:
        self._cron = "*/5 * * * *"
        return self._commit()

    def every_ten_minutes(self) -> ScheduledJob:
        self._cron = "*/10 * * * *"
        return self._commit()

    def every_fifteen_minutes(self) -> ScheduledJob:
        self._cron = "*/15 * * * *"
        return self._commit()

    def every_thirty_minutes(self) -> ScheduledJob:
        self._cron = "*/30 * * * *"
        return self._commit()

    def hourly(self) -> ScheduledJob:
        self._cron = "0 * * * *"
        return self._commit()

    def daily(self) -> ScheduledJob:
        self._cron = "0 0 * * *"
        return self._commit()

    def daily_at(self, time_str: str) -> ScheduledJob:
        hour, minute = _parse_hhmm(time_str)
        self._cron = f"{minute} {hour} * * *"
        return self._commit()

    def weekly(self) -> ScheduledJob:
        self._cron = "0 0 * * 0"
        return self._commit()

    def weekly_on(self, weekday: str, time_str: str) -> ScheduledJob:
        if weekday.lower() not in WEEKDAYS:
            raise SchedulerError(f"Unknown weekday {weekday!r}")
        hour, minute = _parse_hhmm(time_str)
        dow = WEEKDAYS[weekday.lower()]
        self._cron = f"{minute} {hour} * * {dow}"
        return self._commit()

    def monthly(self) -> ScheduledJob:
        self._cron = "0 0 1 * *"
        return self._commit()

    def cron(self, expression: str) -> ScheduledJob:
        self._cron = expression
        return self._commit()

    def without_overlapping(self, ttl: float = 3600.0) -> ScheduledJob:
        """Prevent concurrent runs of the same scheduled job (overlap lock)."""
        self._without_overlapping = True
        self._overlap_ttl = ttl
        return self._recommit()

    def on_one_server(self) -> ScheduledJob:
        """Ensure only one app server dispatches this schedule tick (leader lock)."""
        self._on_one_server = True
        return self._recommit()

    def _commit(self) -> ScheduledJob:
        if self._cron is None:
            raise SchedulerError("Schedule frequency not set")
        entry = ScheduleEntry(
            id=self._entry_id,
            job_name=self._job_name,
            cron=self._cron,
            timezone=self._timezone,
            without_overlapping=self._without_overlapping,
            on_one_server=self._on_one_server,
            overlap_ttl=self._overlap_ttl,
            args=self._args,
            kwargs=self._kwargs,
        )
        self._schedule.app.scheduler_backend.add(entry)
        return self

    def _recommit(self) -> ScheduledJob:
        if self._cron is not None:
            return self._commit()
        return self


def _parse_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != 2:
        raise SchedulerError(f"Invalid time {value!r}; expected HH:MM")
    return int(parts[0]), int(parts[1])


class Schedule:
    """Facade used as ``schedule.job(...).daily_at(...)``."""

    def __init__(self, app: App) -> None:
        self.app = app

    def job(self, job: Job[Any, Any] | Callable[..., Any]) -> ScheduledJob:
        return ScheduledJob(self, job)


def try_dispatch_entry(app: App, entry: ScheduleEntry, *, now: datetime | None = None) -> bool:
    """Dispatch a due schedule entry respecting without_overlapping / on_one_server."""
    now = now or datetime.now(tz=timezone.utc)
    owner = new_lock_owner()
    locks_held: list[tuple[str, str]] = []

    def acquire(key: str, ttl: float) -> bool:
        ok = app.lock_backend.acquire(key, owner=owner, ttl=ttl)
        if ok:
            locks_held.append((key, owner))
        return ok

    try:
        if entry.on_one_server and not acquire(
            f"package_name:schedule:one:{entry.id}", ttl=max(entry.overlap_ttl, 60)
        ):
            return False
        if entry.without_overlapping and not acquire(
            f"package_name:schedule:overlap:{entry.id}", ttl=entry.overlap_ttl
        ):
            return False

        # Resolve job and dispatch
        definition = app.registry.get(entry.job_name)
        from package_name.core.jobs import Job as JobWrapper

        JobWrapper(definition, app=app).dispatch(*entry.args, **entry.kwargs).send()
        entry.last_run_at = now
        return True
    finally:
        # on_one_server lock can be released after dispatch; overlap lock should stay
        # until TTL or explicit release after job completion (MVP: leave overlap TTL).
        for key, own in locks_held:
            if key.startswith("package_name:schedule:one:"):
                app.lock_backend.release(key, owner=own)


__all__ = [
    "Schedule",
    "ScheduleEntry",
    "ScheduledEvent",
    "ScheduledJob",
    "try_dispatch_entry",
]
