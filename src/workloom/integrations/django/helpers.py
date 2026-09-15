"""Django helpers: transaction-aware dispatch."""

from __future__ import annotations

from typing import Any

from workloom.core.jobs import Job, PendingDispatch


def dispatch_after_commit(job: Job[Any, Any], *args: Any, **kwargs: Any) -> None:
    """Dispatch only after the current DB transaction commits.

    Avoids the common bug where a worker sees a job before the row exists.
    """
    from django.db import transaction

    pending = job.dispatch(*args, **kwargs)

    def _send() -> None:
        pending.send()

    transaction.on_commit(_send)


# Monkey-friendly helper attached for docs examples
def install_job_helpers() -> None:
    def _dispatch_after_commit(self: Job[Any, Any], *args: Any, **kwargs: Any) -> None:
        dispatch_after_commit(self, *args, **kwargs)

    Job.dispatch_after_commit = _dispatch_after_commit  # type: ignore[attr-defined]


__all__ = ["PendingDispatch", "dispatch_after_commit", "install_job_helpers"]
