"""Public exception hierarchy for PACKAGE_NAME."""

from __future__ import annotations


class PackageError(Exception):
    """Base error for all PACKAGE_NAME exceptions."""


class ConfigurationError(PackageError):
    """Invalid or incomplete configuration."""


class BackendError(PackageError):
    """Backend failed to perform an operation."""


class DispatchError(PackageError):
    """Job dispatch failed."""


class SerializationError(PackageError):
    """Payload serialization/deserialization failed."""


class JobNotRegisteredError(PackageError):
    """Requested job name is not present in the registry."""


class RetryExhaustedError(PackageError):
    """Job exceeded its maximum retry attempts."""


class LockError(PackageError):
    """Lock acquire/release/refresh failure."""


class UnsupportedCapabilityError(PackageError):
    """Backend does not support the requested capability."""


class StorageError(PackageError):
    """Storage backend failure."""


class SchedulerError(PackageError):
    """Scheduler failure."""


class IdempotencyError(PackageError):
    """Idempotency store conflict or failure."""


__all__ = [
    "BackendError",
    "ConfigurationError",
    "DispatchError",
    "IdempotencyError",
    "JobNotRegisteredError",
    "LockError",
    "PackageError",
    "RetryExhaustedError",
    "SchedulerError",
    "SerializationError",
    "StorageError",
    "UnsupportedCapabilityError",
]
