"""In-memory queue backend with delayed jobs and cancellation."""

from __future__ import annotations

import heapq
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from workloom.contracts.backend import BackendCapabilities
from workloom.core.envelope import JobEnvelope
from workloom.core.executor import execute_envelope
from workloom.core.result import JobHandle, JobStatus
from workloom.exceptions import BackendError

if TYPE_CHECKING:
    from workloom.app import App

_PRIORITY_RANK = {"high": 0, "normal": 1, "low": 2}


@dataclass(order=True)
class _Queued:
    sort_key: tuple[float, int, str]
    envelope: JobEnvelope = field(compare=False)


class MemoryBackend:
    """Realistic queue behavior without external infrastructure."""

    name = "memory"
    capabilities = BackendCapabilities(
        delayed_jobs=True,
        results=True,
        cancellation=True,
        priority=True,
        distributed_locks=False,
        monitoring=True,
        retries=True,
        async_jobs=True,
        chains=True,
        groups=True,
    )

    def __init__(self, app: App | None = None, *, auto_worker: bool = True) -> None:
        self._app = app
        self._auto_worker = auto_worker
        self._queue: list[_Queued] = []
        self._lock = threading.RLock()
        self._wake = threading.Condition(self._lock)
        self._results: dict[str, Any] = {}
        self._status: dict[str, JobStatus] = {}
        self._cancelled: set[str] = set()
        self._worker: threading.Thread | None = None
        self._stopping = False

    def bind(self, app: App) -> MemoryBackend:
        self._app = app
        if self._auto_worker:
            self.start_worker()
        return self

    def start_worker(self) -> None:
        with self._lock:
            if self._worker and self._worker.is_alive():
                return
            self._stopping = False
            self._worker = threading.Thread(
                target=self._run_worker,
                name="workloom-memory-worker",
                daemon=True,
            )
            self._worker.start()

    def stop_worker(self, *, timeout: float = 2.0) -> None:
        with self._wake:
            self._stopping = True
            self._wake.notify_all()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=timeout)

    def dispatch(self, envelope: JobEnvelope) -> JobHandle:
        if self._app is None:
            raise RuntimeError("MemoryBackend is not bound to an App")
        run_at = envelope.run_at or datetime.now(tz=timezone.utc)
        rank = _PRIORITY_RANK.get(envelope.priority, 1)
        item = _Queued(
            sort_key=(run_at.timestamp(), rank, envelope.id),
            envelope=envelope,
        )
        with self._wake:
            heapq.heappush(self._queue, item)
            self._status[envelope.id] = (
                JobStatus.SCHEDULED if envelope.run_at else JobStatus.PENDING
            )
            self._wake.notify()
        if self._auto_worker:
            self.start_worker()
        return JobHandle(id=envelope.id, _backend=self, _app=self._app)

    def get_status(self, job_id: str) -> JobStatus:
        return self._status.get(job_id, JobStatus.UNKNOWN)

    def get_result(self, job_id: str, *, timeout: float | None = None) -> Any:
        deadline = None if timeout is None else time.time() + timeout
        while True:
            with self._lock:
                if job_id in self._cancelled:
                    raise BackendError(f"Job {job_id} was cancelled")
                if self._status.get(job_id) == JobStatus.SUCCEEDED:
                    return self._results[job_id]
                if self._status.get(job_id) == JobStatus.FAILED:
                    raise BackendError(f"Job {job_id} failed")
            if deadline is not None and time.time() >= deadline:
                raise TimeoutError(f"Timed out waiting for job {job_id}")
            time.sleep(0.01)

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            if self._status.get(job_id) in {
                JobStatus.SUCCEEDED,
                JobStatus.FAILED,
                JobStatus.RUNNING,
            }:
                return False
            self._cancelled.add(job_id)
            self._status[job_id] = JobStatus.CANCELLED
            # Remove from heap opportunistically
            self._queue = [q for q in self._queue if q.envelope.id != job_id]
            heapq.heapify(self._queue)
            return True

    def purge(self, queue: str | None = None) -> int:
        with self._lock:
            if queue is None:
                count = len(self._queue)
                self._queue.clear()
                return count
            kept = [q for q in self._queue if q.envelope.queue != queue]
            removed = len(self._queue) - len(kept)
            self._queue = kept
            heapq.heapify(self._queue)
            return removed

    def queue_depth(self, queue: str | None = None) -> int | None:
        with self._lock:
            if queue is None:
                return len(self._queue)
            return sum(1 for q in self._queue if q.envelope.queue == queue)

    def process_due(self, *, now: datetime | None = None) -> int:
        """Process all currently due jobs (useful in tests without the worker)."""
        if self._app is None:
            raise RuntimeError("MemoryBackend is not bound to an App")
        processed = 0
        now = now or datetime.now(tz=timezone.utc)
        while True:
            with self._lock:
                if not self._queue:
                    break
                item = self._queue[0]
                if item.sort_key[0] > now.timestamp():
                    break
                heapq.heappop(self._queue)
                envelope = item.envelope
                if envelope.id in self._cancelled:
                    continue
                self._status[envelope.id] = JobStatus.RUNNING
            try:
                result = execute_envelope(self._app, envelope)
                with self._lock:
                    self._results[envelope.id] = result
                    self._status[envelope.id] = JobStatus.SUCCEEDED
            except Exception:
                with self._lock:
                    self._status[envelope.id] = JobStatus.FAILED
            processed += 1
        return processed

    def _run_worker(self) -> None:
        assert self._app is not None
        while True:
            with self._wake:
                if self._stopping:
                    return
                while not self._queue and not self._stopping:
                    self._wake.wait(timeout=0.1)
                if self._stopping:
                    return
                if not self._queue:
                    continue
                item = self._queue[0]
                now = time.time()
                if item.sort_key[0] > now:
                    self._wake.wait(timeout=min(0.1, item.sort_key[0] - now))
                    continue
                heapq.heappop(self._queue)
                envelope = item.envelope
                if envelope.id in self._cancelled:
                    continue
                self._status[envelope.id] = JobStatus.RUNNING
            try:
                result = execute_envelope(self._app, envelope)
                with self._lock:
                    self._results[envelope.id] = result
                    self._status[envelope.id] = JobStatus.SUCCEEDED
            except Exception:
                with self._lock:
                    self._status[envelope.id] = JobStatus.FAILED


__all__ = ["MemoryBackend"]
