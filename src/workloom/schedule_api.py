"""Module-level schedule proxy bound to the current default app."""

from __future__ import annotations

from typing import Any

from workloom.app import get_current_app
from workloom.schedulers.core import ScheduledJob


class _ScheduleProxy:
    def job(self, job: Any) -> ScheduledJob:
        return get_current_app().schedule.job(job)


schedule = _ScheduleProxy()

__all__ = ["schedule"]
