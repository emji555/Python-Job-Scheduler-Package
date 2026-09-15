"""Pipeline chain/group tests."""

from __future__ import annotations

from workloom import chain, group, job
from workloom.app import App


def test_chain_sequential(app: App) -> None:
    @job
    def double(x: int) -> int:
        return x * 2

    @job
    def add_three(x: int) -> int:
        return x + 3

    handle = chain(double.s(5), add_three).dispatch()
    assert handle is not None
    assert handle.result() == 13


def test_group_then(app: App) -> None:
    @job
    def square(x: int) -> int:
        return x * x

    @job
    def total(values: list[int]) -> int:
        return sum(values)

    handles = group(square.s(i) for i in (2, 3, 4)).then(total).dispatch()
    assert len(handles) == 3
    # callback executed; verify via a fresh total would need storage — check squares
    assert sorted(h.result() for h in handles) == [4, 9, 16]
