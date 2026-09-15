"""Plugin discovery tests."""

from __future__ import annotations

from package_name.plugins import GROUP_BACKENDS, list_plugins, load_plugin


def test_builtin_backends_discoverable() -> None:
    plugins = list_plugins(GROUP_BACKENDS)
    assert "eager" in plugins
    assert "memory" in plugins
    assert "celery" in plugins
    cls = load_plugin(GROUP_BACKENDS, "eager")
    assert cls.__name__ == "EagerBackend"
