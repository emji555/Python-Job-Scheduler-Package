"""Scheduler timezone and fluent API tests."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from workloom import job, schedule
from workloom.app import App
from workloom.schedulers.core import ScheduleEntry


def test_daily_at_cron_and_timezone(app: App) -> None:
    @job
    def nightly() -> str:
        return "ok"

    schedule.job(nightly).daily_at("02:00").timezone("Africa/Cairo")
    entries = app.scheduler_backend.list()
    assert len(entries) == 1
    entry = entries[0]
    assert entry.cron == "0 2 * * *"
    assert entry.timezone == "Africa/Cairo"

    # 01:59 Cairo -> next is 02:00 Cairo
    local = datetime(2026, 1, 15, 1, 59, tzinfo=ZoneInfo("Africa/Cairo"))
    nxt = entry.next_run_after(local)
    assert nxt.astimezone(ZoneInfo("Africa/Cairo")).hour == 2
    assert nxt.tzinfo is not None
    assert nxt.utcoffset() == timezone.utc.utcoffset(nxt)


def test_without_overlapping_and_on_one_server_flags(app: App) -> None:
    @job
    def sync_data() -> None:
        return None

    schedule.job(sync_data).every_five_minutes().without_overlapping().on_one_server()
    entry = app.scheduler_backend.list()[0]
    assert entry.without_overlapping is True
    assert entry.on_one_server is True
    assert isinstance(entry, ScheduleEntry)
