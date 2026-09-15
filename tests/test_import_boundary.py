"""Import boundary: core must not pull optional frameworks/engines."""

from __future__ import annotations

import sys

import workloom


def test_core_import_excludes_optional_deps() -> None:
    forbidden = ["django", "flask", "fastapi", "celery", "redis"]
    loaded = {name.split(".")[0] for name in sys.modules}
    for name in forbidden:
        assert name not in loaded, f"{name} was imported by workloom core"
    assert workloom.__version__
