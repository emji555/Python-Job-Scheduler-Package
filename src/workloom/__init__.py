"""Workloom — Laravel-inspired jobs & scheduling for Python."""

from __future__ import annotations

from workloom.app import App, configure, get_current_app
from workloom.core.context import current_job
from workloom.core.jobs import job
from workloom.core.middleware import LoggingMiddleware
from workloom.exceptions import (
    BackendError,
    ConfigurationError,
    DispatchError,
    JobNotRegisteredError,
    LockError,
    PackageError,
    RetryExhaustedError,
    SerializationError,
    UnsupportedCapabilityError,
)
from workloom.pipelines import chain, group
from workloom.schedule_api import schedule

__version__ = "0.1.0"

__all__ = [
    "App",
    "BackendError",
    "ConfigurationError",
    "DispatchError",
    "JobNotRegisteredError",
    "LockError",
    "LoggingMiddleware",
    "PackageError",
    "RetryExhaustedError",
    "SerializationError",
    "UnsupportedCapabilityError",
    "__version__",
    "chain",
    "configure",
    "current_job",
    "get_current_app",
    "group",
    "job",
    "schedule",
]
