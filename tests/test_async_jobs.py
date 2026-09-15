"""Async job support on eager backend."""

from __future__ import annotations

from workloom import job
from workloom.app import App


def test_async_job_on_eager(app: App) -> None:
    @job
    async def aget(x: int) -> int:
        return x + 1

    assert aget.definition.is_async is True
    assert aget.dispatch(41).result() == 42
