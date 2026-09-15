"""Job decorator and pending dispatch builder."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any, Generic, TypeVar, cast, overload

from package_name.core.envelope import JobEnvelope
from package_name.core.events import JobDispatched
from package_name.core.registry import JobDefinition, detect_async, qualify_name
from package_name.core.result import JobHandle
from package_name.typing import P, R

F = TypeVar("F", bound=Callable[..., Any])


class PendingDispatch(Generic[R]):
    """Fluent builder returned by ``job.dispatch(...)``."""

    def __init__(
        self,
        definition: JobDefinition,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        *,
        app: Any | None = None,
        queue: str | None = None,
        priority: str | None = None,
        delay: timedelta | None = None,
        metadata: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> None:
        self._definition = definition
        self._args = args
        self._kwargs = kwargs
        self._app = app
        self._queue = queue
        self._priority = priority
        self._delay = delay
        self._metadata = dict(metadata or {})
        self._timeout = timeout
        self._handle: JobHandle | None = None
        self._dispatched = False

    def on_queue(self, queue: str) -> PendingDispatch[R]:
        self._queue = queue
        return self

    def priority(self, priority: str) -> PendingDispatch[R]:
        self._priority = priority
        return self

    def delay(
        self,
        *,
        minutes: float = 0,
        seconds: float = 0,
        hours: float = 0,
        days: float = 0,
    ) -> PendingDispatch[R]:
        self._delay = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return self

    def with_metadata(self, **metadata: Any) -> PendingDispatch[R]:
        self._metadata.update(metadata)
        return self

    def _resolve_app(self) -> Any:
        if self._app is not None:
            return self._app
        from package_name.app import get_current_app

        return get_current_app()

    def _build_envelope(self) -> JobEnvelope:
        app = self._resolve_app()
        definition = self._definition
        run_at = None
        if self._delay is not None:
            run_at = datetime.now(tz=timezone.utc) + self._delay

        idem_key: str | None = None
        if definition.idempotency_key is not None:
            if callable(definition.idempotency_key):
                idem_key = definition.idempotency_key(*self._args, **self._kwargs)
            else:
                idem_key = str(definition.idempotency_key)

        return JobEnvelope(
            job=definition.name,
            args=list(self._args),
            kwargs=dict(self._kwargs),
            queue=self._queue or definition.queue or app.settings.default_queue,
            priority=self._priority or definition.priority,
            attempts=0,
            max_attempts=definition.max_attempts,
            run_at=run_at,
            timeout=self._timeout if self._timeout is not None else definition.timeout,
            metadata=self._metadata,
            backoff=definition.backoff,
            retry_on=[e.__name__ for e in definition.retry_on] if definition.retry_on else None,
            dont_retry_on=(
                [e.__name__ for e in definition.dont_retry_on] if definition.dont_retry_on else None
            ),
            idempotency_key=idem_key,
        )

    def _dispatch(self) -> JobHandle:
        if self._dispatched and self._handle is not None:
            return self._handle
        app = self._resolve_app()
        envelope = self._build_envelope()
        if envelope.run_at is not None:
            app.backend.capabilities.require("delayed_jobs")
        priority = self._priority or self._definition.priority
        if priority not in (None, "normal"):
            app.backend.capabilities.require("priority")

        if envelope.idempotency_key:
            existing = app.storage.get_idempotency(envelope.idempotency_key)
            if existing and existing.get("status") == "succeeded":
                prior_id = str(existing.get("job_id") or envelope.id)
                # Skip re-execution; return a handle for the prior successful job.
                return JobHandle(id=prior_id, _backend=app.backend, _app=app)

        stack = app.middleware_stack
        for mw in self._definition.middleware:
            stack = type(stack)([*stack.items, mw])
        envelope = stack.before_dispatch(envelope)
        handle = app.backend.dispatch(envelope)
        stack.after_dispatch(envelope, handle)
        app.events.emit(
            JobDispatched(
                job_id=envelope.id,
                job=envelope.job,
                queue=envelope.queue,
                metadata=dict(envelope.metadata),
            )
        )
        app.record_dispatch()
        self._handle = handle
        self._dispatched = True
        return cast(JobHandle, handle)

    # Auto-dispatch when handle attributes are accessed after chaining,
    # and also allow treating PendingDispatch as the handle itself.
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        handle = self._dispatch()
        return getattr(handle, name)

    @property
    def id(self) -> str:
        return self._dispatch().id

    def status(self) -> Any:
        return self._dispatch().status()

    def result(self, *, timeout: float | None = None) -> Any:
        return self._dispatch().result(timeout=timeout)

    def cancel(self) -> bool:
        return self._dispatch().cancel()

    def send(self) -> JobHandle:
        """Explicitly dispatch and return the handle."""
        return self._dispatch()


class Job(Generic[P, R]):
    """Callable job wrapper preserving the original function."""

    def __init__(self, definition: JobDefinition, *, app: Any | None = None) -> None:
        self.__wrapped__ = definition.func
        self._definition = definition
        self._app = app
        self.__name__ = getattr(definition.func, "__name__", definition.name)
        self.__doc__ = definition.func.__doc__
        self.__module__ = getattr(definition.func, "__module__", "package_name")
        self.__qualname__ = getattr(definition.func, "__qualname__", self.__name__)
        self.__annotations__ = getattr(definition.func, "__annotations__", {})

    @property
    def name(self) -> str:
        return self._definition.name

    @property
    def definition(self) -> JobDefinition:
        return self._definition

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return cast(R, self._definition.func(*args, **kwargs))

    def dispatch(self, *args: P.args, **kwargs: P.kwargs) -> PendingDispatch[R]:
        return PendingDispatch(
            self._definition,
            args,
            dict(kwargs),
            app=self._app,
        )

    def s(self, *args: P.args, **kwargs: P.kwargs) -> PendingDispatch[R]:
        """Signature-style partial for pipelines (not yet dispatched)."""
        return PendingDispatch(self._definition, args, dict(kwargs), app=self._app)


@overload
def job(func: Callable[P, R]) -> Job[P, R]: ...


@overload
def job(
    *,
    name: str | None = None,
    queue: str = "default",
    retries: int = 0,
    timeout: float | None = None,
    backoff: str | int | float = 0,
    jitter: bool = False,
    max_delay: float | None = None,
    retry_on: tuple[type[BaseException], ...] | None = None,
    dont_retry_on: tuple[type[BaseException], ...] | None = None,
    middleware: list[Any] | None = None,
    idempotency_key: Callable[..., str] | str | None = None,
    priority: str = "normal",
    app: Any | None = None,
) -> Callable[[Callable[P, R]], Job[P, R]]: ...


def job(
    func: Callable[P, R] | None = None,
    *,
    name: str | None = None,
    queue: str = "default",
    retries: int = 0,
    timeout: float | None = None,
    backoff: str | int | float = 0,
    jitter: bool = False,
    max_delay: float | None = None,
    retry_on: tuple[type[BaseException], ...] | None = None,
    dont_retry_on: tuple[type[BaseException], ...] | None = None,
    middleware: list[Any] | None = None,
    idempotency_key: Callable[..., str] | str | None = None,
    priority: str = "normal",
    app: Any | None = None,
) -> Job[P, R] | Callable[[Callable[P, R]], Job[P, R]]:
    """Register a function as a background job."""

    def decorator(fn: Callable[P, R]) -> Job[P, R]:
        from package_name.app import get_current_app

        target_app = app if app is not None else get_current_app()
        job_name = name or qualify_name(fn)
        definition = JobDefinition(
            name=job_name,
            func=fn,
            queue=queue,
            retries=retries,
            timeout=timeout,
            backoff=backoff,
            jitter=jitter,
            max_delay=max_delay,
            retry_on=retry_on,
            dont_retry_on=dont_retry_on,
            middleware=list(middleware or []),
            idempotency_key=idempotency_key,
            is_async=detect_async(fn),
            priority=priority,
        )
        target_app.registry.register(definition)
        return Job(definition, app=target_app)

    if func is not None:
        return decorator(func)
    return decorator


__all__ = ["Job", "PendingDispatch", "job"]
