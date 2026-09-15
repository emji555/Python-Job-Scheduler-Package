"""Memory backend contract-ish tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from workloom import job
from workloom.app import App
from workloom.core.result import JobStatus


def test_memory_delayed_and_priority(memory_app: App) -> None:
    results: list[str] = []

    @job
    def push(name: str) -> str:
        results.append(name)
        return name

    later = push.dispatch("late").delay(seconds=60)
    later.send()
    high = push.dispatch("high").priority("high")
    high.send()
    normal = push.dispatch("normal")
    normal.send()

    # Due jobs only (no delay)
    processed = memory_app.backend.process_due()  # type: ignore[attr-defined]
    assert processed == 2
    assert results == ["high", "normal"]
    assert high.status() == JobStatus.SUCCEEDED

    # Advance delayed job
    env_id = later.id
    # Force run_at into the past by processing with future "now"
    future = datetime.now(tz=UTC) + timedelta(minutes=5)
    memory_app.backend.process_due(now=future)  # type: ignore[attr-defined]
    assert "late" in results
    assert memory_app.backend.get_status(env_id) == JobStatus.SUCCEEDED


def test_memory_cancel(memory_app: App) -> None:
    @job
    def slow(x: int) -> int:
        return x

    handle = slow.dispatch(1).delay(minutes=10).send()
    assert handle.cancel() is True
    assert handle.status() == JobStatus.CANCELLED
