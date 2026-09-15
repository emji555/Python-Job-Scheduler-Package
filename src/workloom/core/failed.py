"""Failed-job records and manager API."""

from __future__ import annotations

import builtins
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from workloom.core.envelope import JobEnvelope
from workloom.core.redaction import redact_mapping

if TYPE_CHECKING:
    from workloom.app import App
    from workloom.contracts.storage import StorageBackend


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


@dataclass(slots=True)
class FailedJobRecord:
    id: str
    job_id: str
    job_name: str
    queue: str
    payload: dict[str, Any]
    exception_type: str
    exception_message: str
    traceback: str
    attempts: int
    failed_at: datetime = field(default_factory=_utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["failed_at"] = self.failed_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FailedJobRecord:
        failed_at = data.get("failed_at")
        if isinstance(failed_at, str):
            failed_at = datetime.fromisoformat(failed_at)
        return cls(
            id=str(data["id"]),
            job_id=str(data["job_id"]),
            job_name=str(data["job_name"]),
            queue=str(data.get("queue") or "default"),
            payload=dict(data.get("payload") or {}),
            exception_type=str(data.get("exception_type") or "Exception"),
            exception_message=str(data.get("exception_message") or ""),
            traceback=str(data.get("traceback") or ""),
            attempts=int(data.get("attempts") or 0),
            failed_at=failed_at or _utcnow(),
            metadata=dict(data.get("metadata") or {}),
        )


def build_failed_record(
    envelope: JobEnvelope,
    exc: BaseException,
    *,
    redact_keys: tuple[str, ...] = (),
) -> FailedJobRecord:
    payload = redact_mapping(envelope.to_dict(), redact_keys)
    return FailedJobRecord(
        id=str(uuid.uuid4()),
        job_id=envelope.id,
        job_name=envelope.job,
        queue=envelope.queue,
        payload=payload,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        traceback="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        attempts=envelope.attempts,
        metadata=dict(envelope.metadata),
    )


class FailedJobs:
    """Facade over storage for failed/dead-letter jobs."""

    def __init__(self, app: App) -> None:
        self._app = app

    @property
    def _storage(self) -> StorageBackend:
        return self._app.storage

    def list(self, *, limit: int = 100, offset: int = 0) -> builtins.list[FailedJobRecord]:
        return self._storage.list_failed(limit=limit, offset=offset)

    def get(self, failed_id: str) -> FailedJobRecord | None:
        return self._storage.get_failed(failed_id)

    def delete(self, failed_id: str) -> bool:
        return self._storage.delete_failed(failed_id)

    def retry(self, failed_id: str) -> Any:
        record = self.get(failed_id)
        if record is None:
            raise KeyError(failed_id)
        envelope = JobEnvelope.from_dict(record.payload)
        envelope.attempts = 0
        envelope.id = envelope.id  # keep original id for correlation
        handle = self._app.backend.dispatch(envelope)
        self.delete(failed_id)
        return handle

    def retry_all(self) -> builtins.list[Any]:
        handles: builtins.list[Any] = []
        for record in self.list(limit=10_000):
            handles.append(self.retry(record.id))
        return handles


__all__ = ["FailedJobRecord", "FailedJobs", "build_failed_record"]
