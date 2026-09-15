"""Middleware and events."""

from __future__ import annotations

from package_name import job
from package_name.app import App
from package_name.core.events import JobDispatched, JobSucceeded
from package_name.core.middleware import LoggingMiddleware


def test_middleware_and_events(app: App) -> None:
    seen: list[str] = []

    app.events.on(JobDispatched, lambda e: seen.append(f"dispatched:{e.job}"))
    app.events.on(JobSucceeded, lambda e: seen.append(f"succeeded:{e.job}"))
    app.middleware_stack.add(LoggingMiddleware())

    @job
    def hello(name: str) -> str:
        return f"hi {name}"

    assert hello.dispatch("Eslam").result() == "hi Eslam"
    assert any(s.startswith("dispatched:") for s in seen)
    assert any(s.startswith("succeeded:") for s in seen)
