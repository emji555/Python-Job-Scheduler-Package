"""Job middleware hooks."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from workloom.core.envelope import JobEnvelope


@runtime_checkable
class Middleware(Protocol):
    def before_dispatch(self, envelope: JobEnvelope) -> JobEnvelope:
        return envelope

    def after_dispatch(self, envelope: JobEnvelope, handle: Any) -> None:
        return None

    def before_execute(self, envelope: JobEnvelope) -> JobEnvelope:
        return envelope

    def after_execute(self, envelope: JobEnvelope, result: Any) -> Any:
        return result

    def on_success(self, envelope: JobEnvelope, result: Any) -> None:
        return None

    def on_failure(self, envelope: JobEnvelope, exc: BaseException) -> None:
        return None

    def on_retry(self, envelope: JobEnvelope, exc: BaseException, delay: float) -> None:
        return None


class MiddlewareStack:
    def __init__(self, middleware: list[Middleware] | None = None) -> None:
        self._items: list[Middleware] = list(middleware or [])

    def add(self, middleware: Middleware) -> None:
        self._items.append(middleware)

    def extend(self, middleware: list[Middleware]) -> None:
        self._items.extend(middleware)

    @property
    def items(self) -> list[Middleware]:
        return list(self._items)

    def before_dispatch(self, envelope: JobEnvelope) -> JobEnvelope:
        for mw in self._items:
            envelope = mw.before_dispatch(envelope)
        return envelope

    def after_dispatch(self, envelope: JobEnvelope, handle: Any) -> None:
        for mw in self._items:
            mw.after_dispatch(envelope, handle)

    def before_execute(self, envelope: JobEnvelope) -> JobEnvelope:
        for mw in self._items:
            envelope = mw.before_execute(envelope)
        return envelope

    def after_execute(self, envelope: JobEnvelope, result: Any) -> Any:
        for mw in self._items:
            result = mw.after_execute(envelope, result)
        return result

    def on_success(self, envelope: JobEnvelope, result: Any) -> None:
        for mw in self._items:
            mw.on_success(envelope, result)

    def on_failure(self, envelope: JobEnvelope, exc: BaseException) -> None:
        for mw in self._items:
            mw.on_failure(envelope, exc)

    def on_retry(self, envelope: JobEnvelope, exc: BaseException, delay: float) -> None:
        for mw in self._items:
            mw.on_retry(envelope, exc, delay)


class LoggingMiddleware:
    """Example middleware that logs lifecycle transitions."""

    def __init__(self, logger: Any | None = None) -> None:
        import logging

        self._logger = logger or logging.getLogger("workloom.middleware")

    def before_dispatch(self, envelope: JobEnvelope) -> JobEnvelope:
        self._logger.info(
            "dispatch job=%s id=%s queue=%s", envelope.job, envelope.id, envelope.queue
        )
        return envelope

    def after_dispatch(self, envelope: JobEnvelope, handle: Any) -> None:
        return None

    def before_execute(self, envelope: JobEnvelope) -> JobEnvelope:
        self._logger.info(
            "execute job=%s id=%s attempt=%s",
            envelope.job,
            envelope.id,
            envelope.attempts + 1,
        )
        return envelope

    def after_execute(self, envelope: JobEnvelope, result: Any) -> Any:
        return result

    def on_success(self, envelope: JobEnvelope, result: Any) -> None:
        self._logger.info("success job=%s id=%s", envelope.job, envelope.id)

    def on_failure(self, envelope: JobEnvelope, exc: BaseException) -> None:
        self._logger.error("failure job=%s id=%s error=%s", envelope.job, envelope.id, exc)

    def on_retry(self, envelope: JobEnvelope, exc: BaseException, delay: float) -> None:
        self._logger.warning(
            "retry job=%s id=%s delay=%s error=%s",
            envelope.job,
            envelope.id,
            delay,
            exc,
        )


__all__ = ["LoggingMiddleware", "Middleware", "MiddlewareStack"]
