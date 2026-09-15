"""Retry policy helpers."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff: str | int | float = 0
    jitter: bool = False
    max_delay: float | None = None
    retry_on: tuple[type[BaseException], ...] | None = None
    dont_retry_on: tuple[type[BaseException], ...] | None = None

    def should_retry(self, attempt: int, exc: BaseException) -> bool:
        if attempt >= self.max_attempts:
            return False
        if self.dont_retry_on and isinstance(exc, self.dont_retry_on):
            return False
        return not (self.retry_on is not None and not isinstance(exc, self.retry_on))

    def delay_seconds(self, attempt: int) -> float:
        """Compute delay before the next attempt (attempt is 1-based after failure)."""
        if isinstance(self.backoff, (int, float)):
            delay = float(self.backoff)
        elif self.backoff == "exponential":
            delay = float(2 ** max(attempt - 1, 0))
        else:
            try:
                delay = float(self.backoff)
            except (TypeError, ValueError):
                delay = 0.0
        if self.jitter and delay > 0:
            delay = delay * (0.5 + random.random())
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)
        return max(delay, 0.0)

    def to_metadata(self) -> dict[str, Any]:
        return {
            "max_attempts": self.max_attempts,
            "backoff": self.backoff,
            "jitter": self.jitter,
            "max_delay": self.max_delay,
            "retry_on": [exc.__name__ for exc in self.retry_on] if self.retry_on else None,
            "dont_retry_on": (
                [exc.__name__ for exc in self.dont_retry_on] if self.dont_retry_on else None
            ),
        }


__all__ = ["RetryPolicy"]
