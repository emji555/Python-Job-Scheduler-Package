"""Shared fixtures."""

from __future__ import annotations

import pytest

from package_name.app import App, reset_default_app, set_current_app


@pytest.fixture(autouse=True)
def _isolate_app() -> None:
    reset_default_app()
    yield
    reset_default_app()


@pytest.fixture
def app() -> App:
    application = App(backend="eager")
    set_current_app(application)
    return application


@pytest.fixture
def memory_app() -> App:
    application = App(backend="memory")
    # Deterministic tests: disable auto worker; call process_due manually
    application.backend._auto_worker = False  # type: ignore[attr-defined]
    if hasattr(application.backend, "stop_worker"):
        application.backend.stop_worker()  # type: ignore[attr-defined]
    set_current_app(application)
    return application
