"""Versioned job envelope — backend-independent wire format."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from workloom.exceptions import SerializationError

ENVELOPE_VERSION = 1


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def new_job_id() -> str:
    return str(uuid.uuid4())


@dataclass(slots=True)
class JobEnvelope:
    """Backend-independent job message.

    Wire format is versioned. Prefer JSON-safe args/kwargs.
    """

    job: str
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=new_job_id)
    version: int = ENVELOPE_VERSION
    queue: str = "default"
    priority: str = "normal"
    attempts: int = 0
    max_attempts: int = 1
    created_at: datetime = field(default_factory=_utcnow)
    run_at: datetime | None = None
    timeout: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    backoff: str | int | float | None = None
    retry_on: list[str] | None = None
    dont_retry_on: list[str] | None = None
    idempotency_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["run_at"] = self.run_at.isoformat() if self.run_at else None
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobEnvelope:
        version = int(data.get("version", ENVELOPE_VERSION))
        if version != ENVELOPE_VERSION:
            raise SerializationError(
                f"Unsupported envelope version {version}; expected {ENVELOPE_VERSION}"
            )
        created_at = data.get("created_at")
        run_at = data.get("run_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if isinstance(run_at, str):
            run_at = datetime.fromisoformat(run_at)
        return cls(
            version=version,
            id=str(data["id"]),
            job=str(data["job"]),
            args=list(data.get("args") or []),
            kwargs=dict(data.get("kwargs") or {}),
            queue=str(data.get("queue") or "default"),
            priority=str(data.get("priority") or "normal"),
            attempts=int(data.get("attempts") or 0),
            max_attempts=int(data.get("max_attempts") or 1),
            created_at=created_at or _utcnow(),
            run_at=run_at,
            timeout=data.get("timeout"),
            metadata=dict(data.get("metadata") or {}),
            backoff=data.get("backoff"),
            retry_on=list(data["retry_on"]) if data.get("retry_on") else None,
            dont_retry_on=list(data["dont_retry_on"]) if data.get("dont_retry_on") else None,
            idempotency_key=data.get("idempotency_key"),
        )


__all__ = ["ENVELOPE_VERSION", "JobEnvelope", "new_job_id"]
