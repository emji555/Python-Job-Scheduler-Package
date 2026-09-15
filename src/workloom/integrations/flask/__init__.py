"""Optional Flask integration helpers."""

from __future__ import annotations

from typing import Any

from workloom.app import App, configure, get_current_app


def init_app(flask_app: Any, **config: Any) -> App:
    """Initialize Workloom on a Flask app."""
    package_app = configure(**config)
    flask_app.extensions = getattr(flask_app, "extensions", {})
    flask_app.extensions["workloom"] = package_app

    @flask_app.teardown_appcontext
    def _teardown(exception: BaseException | None) -> None:
        # Keep default app; no per-request state required for MVP
        return None

    return package_app


def current_package_app() -> App:
    try:
        from flask import current_app

        ext = current_app.extensions.get("workloom")
        if ext is not None:
            return ext  # type: ignore[no-any-return]
    except Exception:
        pass
    return get_current_app()


__all__ = ["current_package_app", "init_app"]
