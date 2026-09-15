"""Backend contract tests — shared semantics across backends."""

from __future__ import annotations

import pytest

from package_name.app import App, set_current_app
from package_name.core.jobs import job
from package_name.core.result import JobStatus


@pytest.fixture(params=["eager", "memory"])
def contract_app(request: pytest.FixtureRequest) -> App:
    app = App(backend=request.param)
    if request.param == "memory":
        app.backend._auto_worker = False  # type: ignore[attr-defined]
        app.backend.stop_worker()  # type: ignore[attr-defined]
    set_current_app(app)
    return app


def test_contract_dispatch_and_result(contract_app: App) -> None:
    @job
    def mul(a: int, b: int) -> int:
        return a * b

    handle = mul.dispatch(6, 7).send()
    if contract_app.backend.name == "memory":
        contract_app.backend.process_due()  # type: ignore[attr-defined]
    assert handle.result(timeout=2) == 42
    assert handle.status() == JobStatus.SUCCEEDED


def test_contract_capabilities_object(contract_app: App) -> None:
    caps = contract_app.backend.capabilities
    assert caps.retries is True
    assert hasattr(caps, "delayed_jobs")
