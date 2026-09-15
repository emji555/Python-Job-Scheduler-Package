"""PACKAGE_NAME — Laravel-inspired jobs & scheduling for Python.

Temporary public names:
- Distribution: ``package-name``
- Import: ``package_name``
Rename before the first PyPI release.
"""

from __future__ import annotations

from package_name.app import App, configure, get_current_app
from package_name.core.context import current_job
from package_name.core.jobs import job
from package_name.core.middleware import LoggingMiddleware
from package_name.exceptions import (
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
from package_name.pipelines import chain, group
from package_name.schedule_api import schedule

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
