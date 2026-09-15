"""Serialization and envelope tests."""

from __future__ import annotations

import pytest

from package_name.core.envelope import JobEnvelope
from package_name.exceptions import SerializationError
from package_name.serializers import JsonSerializer


def test_json_roundtrip() -> None:
    ser = JsonSerializer()
    envelope = JobEnvelope(job="demo.job", args=[1, "x"], kwargs={"ok": True})
    raw = ser.dumps(envelope.to_dict())
    data = ser.loads(raw)
    restored = JobEnvelope.from_dict(data)
    assert restored.job == "demo.job"
    assert restored.args == [1, "x"]
    assert restored.kwargs == {"ok": True}


def test_rejects_non_json() -> None:
    ser = JsonSerializer()
    with pytest.raises(SerializationError):
        ser.dumps({"fn": lambda: None})  # type: ignore[dict-item]
