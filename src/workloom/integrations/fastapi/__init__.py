"""Optional FastAPI integration helpers."""

from __future__ import annotations

from typing import Any

from workloom.app import App, configure


def create_app(**config: Any) -> App:
    """Configure Workloom during FastAPI lifespan startup."""
    return configure(**config)


def install_lifespan(fastapi_app: Any, **config: Any) -> Any:
    """Attach startup/shutdown hooks to a FastAPI application."""
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(app: Any):
        package_app = create_app(**config)
        app.state.workloom = package_app
        if hasattr(package_app.scheduler_backend, "start"):
            # Do not auto-start scheduler unless asked
            pass
        yield
        backend = package_app.backend
        if hasattr(backend, "stop_worker"):
            backend.stop_worker()  # type: ignore[attr-defined]
        package_app.scheduler_backend.stop()

    fastapi_app.router.lifespan_context = lifespan
    return fastapi_app


def get_app(request: Any) -> App:
    return request.app.state.workloom  # type: ignore[no-any-return]


__all__ = ["create_app", "get_app", "install_lifespan"]
