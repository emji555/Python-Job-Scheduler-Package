"""In-process poll-based scheduler."""

from __future__ import annotations

import builtins
import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from workloom.schedulers.core import ScheduledEvent, ScheduleEntry, try_dispatch_entry

if TYPE_CHECKING:
    from workloom.app import App

logger = logging.getLogger(__name__)


class InProcessScheduler:
    name = "inprocess"

    def __init__(self, app: App | None = None, *, poll_interval: float = 1.0) -> None:
        self._app = app
        self._entries: dict[str, ScheduleEntry] = {}
        self._poll_interval = poll_interval
        self._thread: threading.Thread | None = None
        self._stopping = False
        self._lock = threading.RLock()
        self._last_tick: dict[str, datetime] = {}

    def bind(self, app: App) -> InProcessScheduler:
        self._app = app
        return self

    def add(self, entry: ScheduleEntry) -> None:
        with self._lock:
            self._entries[entry.id] = entry

    def remove(self, entry_id: str) -> bool:
        with self._lock:
            return self._entries.pop(entry_id, None) is not None

    def list(self) -> builtins.list[ScheduleEntry]:
        with self._lock:
            return list(self._entries.values())

    def tick(self, *, now: datetime | None = None) -> builtins.list[ScheduledEvent]:
        if self._app is None:
            raise RuntimeError("InProcessScheduler is not bound to an App")
        now = now or datetime.now(tz=timezone.utc)
        due: builtins.list[ScheduledEvent] = []
        with self._lock:
            entries = list(self._entries.values())
        for entry in entries:
            last = self._last_tick.get(entry.id)
            probe = last or (now - timedelta(seconds=1))
            nxt = entry.next_run_after(probe)
            if nxt <= now:
                window_key = nxt.replace(second=0, microsecond=0)
                fired_marker = self._last_tick.get(entry.id)
                if fired_marker is not None and fired_marker >= window_key:
                    continue
                due.append(ScheduledEvent(entry=entry, due_at=nxt))
                self._last_tick[entry.id] = window_key
                try_dispatch_entry(self._app, entry, now=now)
        return due

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stopping = False
        self._thread = threading.Thread(
            target=self._loop,
            name="workloom-scheduler",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stopping = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _loop(self) -> None:
        while not self._stopping:
            try:
                self.tick()
            except Exception:
                logger.exception("Scheduler tick failed")
            time.sleep(self._poll_interval)


__all__ = ["InProcessScheduler"]
