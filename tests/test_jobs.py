"""Core job decorator and eager backend tests."""

from __future__ import annotations

import pytest

from workloom import job
from workloom.app import App, set_current_app
from workloom.core.result import JobStatus
from workloom.exceptions import RetryExhaustedError, UnsupportedCapabilityError


def test_eager_dispatch_returns_result(app: App) -> None:
    @job
    def add(a: int, b: int) -> int:
        return a + b

    handle = add.dispatch(2, 3)
    assert handle.result() == 5
    assert handle.status() == JobStatus.SUCCEEDED


def test_job_config_queue_and_retries(app: App) -> None:
    calls: list[int] = []

    @job(queue="dhis2", retries=2, backoff=0)
    def flaky(x: int) -> int:
        calls.append(x)
        if len(calls) < 3:
            raise ConnectionError("boom")
        return x

    assert flaky.dispatch(7).result() == 7
    assert len(calls) == 3
    assert flaky.definition.queue == "dhis2"


def test_retry_exhausted_records_failed_job(app: App) -> None:
    @job(retries=1, backoff=0)
    def always_fail() -> None:
        raise RuntimeError("nope")

    with pytest.raises(RetryExhaustedError):
        always_fail.dispatch().result()
    failed = app.failed_jobs.list()
    assert len(failed) == 1
    assert failed[0].job_name.endswith("always_fail")


def test_unsupported_delay_on_eager(app: App) -> None:
    @job
    def ping() -> str:
        return "pong"

    with pytest.raises(UnsupportedCapabilityError):
        ping.dispatch().delay(seconds=1).send()


def test_current_job_context(app: App) -> None:
    from workloom import current_job

    seen: dict[str, object] = {}

    @job
    def inspect() -> str:
        seen["id"] = current_job.id
        seen["attempt"] = current_job.attempt
        seen["queue"] = current_job.queue
        return "ok"

    handle = inspect.dispatch()
    assert handle.result() == "ok"
    assert seen["id"] == handle.id
    assert seen["attempt"] == 1
    assert seen["queue"] == "default"


def test_multiple_apps_isolated() -> None:
    a = App(backend="eager")
    b = App(backend="eager")
    set_current_app(a)

    @job(app=a)
    def only_a() -> str:
        return "a"

    assert a.registry.has(only_a.name)
    assert not b.registry.has(only_a.name)
