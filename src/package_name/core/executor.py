"""Job execution helpers shared by backends."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any

from package_name.core.context import JobContext, push_job_context, reset_job_context
from package_name.core.envelope import JobEnvelope
from package_name.core.events import JobFailed, JobRetrying, JobStarted, JobSucceeded
from package_name.core.failed import build_failed_record
from package_name.core.retries import RetryPolicy
from package_name.exceptions import JobNotRegisteredError, RetryExhaustedError

if TYPE_CHECKING:
    from package_name.app import App

logger = logging.getLogger(__name__)


def _run_maybe_async(func: Any, *args: Any, **kwargs: Any) -> Any:
    if asyncio.iscoroutinefunction(func):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(func(*args, **kwargs))
        # Already in an event loop — schedule and wait via a new loop in a thread is
        # complex; for MVP require callers to use async-capable backends or no running loop.
        raise RuntimeError(
            "Async jobs cannot be executed from a running event loop via sync backends; "
            "use an async-capable backend or call from a sync context."
        )
        _ = loop  # pragma: no cover
    return func(*args, **kwargs)


def execute_envelope(app: App, envelope: JobEnvelope) -> Any:
    """Execute a registered job with middleware, events, retries, and failure recording."""
    try:
        definition = app.registry.get(envelope.job)
    except JobNotRegisteredError:
        raise

    policy = definition.retry_policy()
    # Envelope may carry overrides from dispatch-time config
    if envelope.max_attempts:
        policy = RetryPolicy(
            max_attempts=envelope.max_attempts,
            backoff=envelope.backoff if envelope.backoff is not None else policy.backoff,
            jitter=policy.jitter,
            max_delay=policy.max_delay,
            retry_on=policy.retry_on,
            dont_retry_on=policy.dont_retry_on,
        )

    stack = app.middleware_stack
    for mw in definition.middleware:
        stack = type(stack)([*stack.items, mw])

    last_exc: BaseException | None = None
    attempt = max(envelope.attempts, 0)

    while attempt < policy.max_attempts:
        attempt += 1
        envelope.attempts = attempt
        working = stack.before_execute(envelope)
        ctx = JobContext(
            id=working.id,
            job=working.job,
            attempt=attempt,
            queue=working.queue,
            metadata=dict(working.metadata),
            max_attempts=policy.max_attempts,
        )
        token = push_job_context(ctx)
        app.events.emit(JobStarted(job_id=working.id, job=working.job, attempt=attempt))
        try:
            result = _run_maybe_async(definition.func, *working.args, **working.kwargs)
            result = stack.after_execute(working, result)
            stack.on_success(working, result)
            app.events.emit(JobSucceeded(job_id=working.id, job=working.job, result=result))
            app.record_success()
            if working.idempotency_key:
                app.storage.set_idempotency(
                    working.idempotency_key,
                    {"status": "succeeded", "job_id": working.id},
                    ttl=float(working.metadata.get("idempotency_ttl", 86400)),
                )
            return result
        except BaseException as exc:
            last_exc = exc
            stack.on_failure(working, exc)
            app.events.emit(
                JobFailed(job_id=working.id, job=working.job, exception=exc, attempt=attempt)
            )
            if policy.should_retry(attempt, exc):
                delay = policy.delay_seconds(attempt)
                stack.on_retry(working, exc, delay)
                app.events.emit(
                    JobRetrying(
                        job_id=working.id,
                        job=working.job,
                        attempt=attempt,
                        delay=delay,
                        exception=exc,
                    )
                )
                app.record_retry()
                if delay > 0:
                    time.sleep(delay)
                continue
            record = build_failed_record(working, exc, redact_keys=app.settings.redact_keys)
            app.storage.save_failed(record)
            app.record_failure()
            raise RetryExhaustedError(
                f"Job {working.job!r} failed after {attempt} attempt(s): {exc}"
            ) from exc
        finally:
            reset_job_context(token)

    assert last_exc is not None
    raise RetryExhaustedError(str(last_exc)) from last_exc


__all__ = ["execute_envelope"]
