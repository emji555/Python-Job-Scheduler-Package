"""Celery adapter — first production distributed backend."""

from __future__ import annotations

from datetime import timezone
from typing import TYPE_CHECKING, Any

from workloom.contracts.backend import BackendCapabilities
from workloom.core.envelope import JobEnvelope
from workloom.core.executor import execute_envelope
from workloom.core.result import JobHandle, JobStatus
from workloom.exceptions import ConfigurationError, UnsupportedCapabilityError

if TYPE_CHECKING:
    from workloom.app import App


class CeleryBackend:
    """Delegates execution to Celery without exposing Celery objects in the public API."""

    name = "celery"
    capabilities = BackendCapabilities(
        delayed_jobs=True,
        results=True,
        cancellation=True,
        priority=True,
        distributed_locks=False,
        monitoring=False,
        retries=True,
        async_jobs=False,
        chains=False,
        groups=False,
    )

    def __init__(
        self,
        app: App | None = None,
        *,
        broker_url: str | None = None,
        result_backend: str | None = None,
        celery_app: Any | None = None,
    ) -> None:
        self._app = app
        self._broker_url = broker_url
        self._result_backend = result_backend
        self._celery = celery_app
        self._task = None
        self._async_results: dict[str, Any] = {}

    def bind(self, app: App) -> CeleryBackend:
        self._app = app
        if self._broker_url is None:
            self._broker_url = app.settings.broker_url
        if self._result_backend is None:
            self._result_backend = app.settings.result_backend or self._broker_url
        self._ensure_celery()
        return self

    def _ensure_celery(self) -> Any:
        if self._celery is not None:
            return self._celery
        try:
            from celery import Celery
        except ImportError as exc:
            raise ConfigurationError(
                "CeleryBackend requires the 'celery' extra: pip install 'workloom[celery]'"
            ) from exc
        if not self._broker_url:
            raise ConfigurationError("CeleryBackend requires broker_url / WORKLOOM_BROKER_URL")
        self._celery = Celery("workloom", broker=self._broker_url, backend=self._result_backend)

        backend_self = self

        @self._celery.task(name="workloom.execute_envelope", bind=True)  # type: ignore[misc]
        def execute_task(self_task: Any, payload: dict[str, Any]) -> Any:
            _ = self_task
            if backend_self._app is None:
                raise RuntimeError("CeleryBackend is not bound to an App")
            envelope = JobEnvelope.from_dict(payload)
            return execute_envelope(backend_self._app, envelope)

        self._task = execute_task
        return self._celery

    def dispatch(self, envelope: JobEnvelope) -> JobHandle:
        if self._app is None:
            raise RuntimeError("CeleryBackend is not bound to an App")
        self._ensure_celery()
        assert self._task is not None
        options: dict[str, Any] = {"task_id": envelope.id, "queue": envelope.queue}
        if envelope.run_at is not None:
            eta = envelope.run_at
            if eta.tzinfo is None:
                eta = eta.replace(tzinfo=timezone.utc)
            options["eta"] = eta
        if envelope.priority and envelope.priority != "normal":
            # Celery priority is broker-dependent; map coarsely.
            options["priority"] = {"high": 0, "normal": 5, "low": 9}.get(envelope.priority, 5)
        async_result = self._task.apply_async(args=[envelope.to_dict()], **options)
        self._async_results[envelope.id] = async_result
        return JobHandle(id=envelope.id, _backend=self, _app=self._app)

    def get_status(self, job_id: str) -> JobStatus:
        result = self._async_results.get(job_id)
        if result is None:
            self._ensure_celery()
            assert self._celery is not None
            from celery.result import AsyncResult

            result = AsyncResult(job_id, app=self._celery)
        state = result.state
        mapping = {
            "PENDING": JobStatus.PENDING,
            "STARTED": JobStatus.RUNNING,
            "SUCCESS": JobStatus.SUCCEEDED,
            "FAILURE": JobStatus.FAILED,
            "RETRY": JobStatus.RETRYING,
            "REVOKED": JobStatus.CANCELLED,
        }
        return mapping.get(state, JobStatus.UNKNOWN)

    def get_result(self, job_id: str, *, timeout: float | None = None) -> Any:
        result = self._async_results.get(job_id)
        if result is None:
            self._ensure_celery()
            assert self._celery is not None
            from celery.result import AsyncResult

            result = AsyncResult(job_id, app=self._celery)
        return result.get(timeout=timeout)

    def cancel(self, job_id: str) -> bool:
        self._ensure_celery()
        assert self._celery is not None
        self._celery.control.revoke(job_id, terminate=False)
        return True

    def purge(self, queue: str | None = None) -> int:
        _ = queue
        raise UnsupportedCapabilityError("CeleryBackend.purge is not implemented in 0.1")

    def queue_depth(self, queue: str | None = None) -> int | None:
        _ = queue
        return None


__all__ = ["CeleryBackend"]
