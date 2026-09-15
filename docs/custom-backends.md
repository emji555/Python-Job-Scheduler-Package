# Writing a custom backend

This tutorial shows how to ship `workloom-mybackend` without modifying the main repository.

## 1. Implement the contract

```python
# mybackend/backend.py
from workloom.contracts.backend import BackendCapabilities
from workloom.core.envelope import JobEnvelope
from workloom.core.result import JobHandle, JobStatus

class MyBackend:
    name = "mybackend"
    capabilities = BackendCapabilities(results=True, retries=True)

    def __init__(self, app=None, **kwargs):
        self._app = app

    def bind(self, app):
        self._app = app
        return self

    def dispatch(self, envelope: JobEnvelope) -> JobHandle:
        ...
        return JobHandle(id=envelope.id, _backend=self, _app=self._app)

    def get_status(self, job_id: str) -> JobStatus:
        ...

    def get_result(self, job_id: str, *, timeout=None):
        ...

    def cancel(self, job_id: str) -> bool:
        ...

    def purge(self, queue=None) -> int:
        return 0

    def queue_depth(self, queue=None):
        return None
```

## 2. Register an entry point

```toml
# pyproject.toml
[project.entry-points."workloom.backends"]
mybackend = "mybackend.backend:MyBackend"
```

## 3. Install and configure

```bash
pip install workloom-mybackend
```

```python
from workloom import configure
configure(backend="mybackend")
```

## 4. Test against shared semantics

Reuse patterns from `tests/test_backend_contract.py`:

- dispatch + result
- capability object present
- unsupported features raise `UnsupportedCapabilityError`
