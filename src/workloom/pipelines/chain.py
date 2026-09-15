"""Chain and group pipeline primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from workloom.app import get_current_app
from workloom.core.jobs import Job, PendingDispatch
from workloom.core.result import JobHandle
from workloom.exceptions import UnsupportedCapabilityError


@dataclass
class Chain:
    steps: list[Any] = field(default_factory=list)
    _app: Any | None = None

    def dispatch(self) -> JobHandle | None:
        app = self._app or get_current_app()
        if not app.backend.capabilities.chains:
            raise UnsupportedCapabilityError("Backend does not support chains")
        # 0.1: emulate sequentially at the abstraction layer for eager/memory.
        last_handle: JobHandle | None = None
        previous_result: Any = None
        first = True
        for step in self.steps:
            handle = _dispatch_step(step, previous_result, first=first, app=app)
            first = False
            if app.backend.capabilities.results:
                previous_result = handle.result()
            last_handle = handle
        return last_handle


@dataclass
class Group:
    steps: list[Any] = field(default_factory=list)
    _then: Any | None = None
    _app: Any | None = None

    def then(self, callback: Any) -> Group:
        self._then = callback
        return self

    def dispatch(self) -> list[JobHandle]:
        app = self._app or get_current_app()
        if not app.backend.capabilities.groups:
            raise UnsupportedCapabilityError("Backend does not support groups")
        handles = [_dispatch_step(step, None, first=True, app=app) for step in self.steps]
        if self._then is not None:
            results = []
            if app.backend.capabilities.results:
                results = [h.result() for h in handles]
            _dispatch_step(self._then, results, first=False, app=app)
        return handles


def chain(*steps: Any, app: Any | None = None) -> Chain:
    return Chain(steps=list(steps), _app=app)


def group(*steps: Any, app: Any | None = None) -> Group:
    # Allow group(generator)
    if (
        len(steps) == 1
        and not isinstance(steps[0], (Job, PendingDispatch))
        and hasattr(steps[0], "__iter__")
    ):
        steps = tuple(steps[0])  # type: ignore[assignment]
    return Group(steps=list(steps), _app=app)


def _dispatch_step(step: Any, previous: Any, *, first: bool, app: Any) -> JobHandle:
    if isinstance(step, PendingDispatch):
        if not first and previous is not None and not step._args:
            # Feed previous result as first arg when signature was empty
            step._args = (previous,)
        return step.send()
    if isinstance(step, Job):
        if first or previous is None:
            return step.dispatch().send()
        return step.dispatch(previous).send()
    if callable(step):
        # Unregistered callable — execute inline via temporary registration path
        result = step(previous) if not first and previous is not None else step()
        # Wrap as already-completed via eager path is awkward; create a tiny job
        from workloom.backends.eager import EagerBackend
        from workloom.core.envelope import JobEnvelope
        from workloom.core.result import JobStatus

        backend = app.backend
        envelope = JobEnvelope(job="inline", args=[], kwargs={})
        if isinstance(backend, EagerBackend):
            backend._results[envelope.id] = result
            backend._status[envelope.id] = JobStatus.SUCCEEDED
            return JobHandle(id=envelope.id, _backend=backend, _app=app)
        # For other backends, just run and store if memory
        handle_id = envelope.id
        if hasattr(backend, "_results"):
            backend._results[handle_id] = result  # type: ignore[attr-defined]
            backend._status[handle_id] = JobStatus.SUCCEEDED  # type: ignore[attr-defined]
            return JobHandle(id=handle_id, _backend=backend, _app=app)
        raise TypeError(f"Unsupported pipeline step type: {type(step)!r}")
    raise TypeError(f"Unsupported pipeline step type: {type(step)!r}")


__all__ = ["Chain", "Group", "chain", "group"]
