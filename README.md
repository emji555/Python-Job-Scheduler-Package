# Workloom

Laravel-inspired **jobs, queues, scheduling, retries, locks, failed jobs, pipelines, and monitoring** for the Python ecosystem — without coupling your application to Django, FastAPI, Flask, Celery, or any single task engine.

| | |
|---|---|
| PyPI | `workloom` |
| Import | `from workloom import job` |
| CLI | `workloom` |
| Env | `WORKLOOM_*` |

## Install

```bash
pip install workloom
```

Optional extras:

```bash
pip install "workloom[celery]"
pip install "workloom[redis]"
pip install "workloom[django]"
pip install "workloom[fastapi]"
pip install "workloom[flask]"
```

## Quick start

```python
from workloom import job

@job
def send_email(user_id: int) -> None:
    print(user_id)

send_email.dispatch(10)
```

## Production-shaped example

```python
from workloom import configure, job, schedule

configure(
    backend="celery",
    broker_url="redis://localhost:6379/0",
    timezone="Africa/Cairo",
)

@job(queue="dhis2", retries=5, backoff="exponential", timeout=120)
def sync_patient(patient_id: int) -> None:
    ...

sync_patient.dispatch(15).on_queue("dhis2")

schedule.job(sync_patient).every_five_minutes().without_overlapping()
```

Swap backends without rewriting business functions:

```text
EagerBackend | MemoryBackend | CeleryBackend | (community backends)
```

## Why this library exists

Python teams often hard-wire Celery or Django-Q into domain code. `Workloom` gives you a stable Laravel-like API and a plugin architecture around proven engines — not a new broker.

See [docs/architecture.md](docs/architecture.md).

## CLI

```bash
workloom doctor
workloom worker
workloom schedule run
workloom schedule list
workloom queues
workloom jobs failed
workloom jobs retry --all
```

## Documentation

- Architecture: `docs/architecture.md`
- ADRs: `docs/adr/`
- Custom backends: `docs/custom-backends.md`
- Security: `SECURITY.md` / `docs/security.md`
- Releasing: `docs/releasing.md`
- Full docs site: MkDocs Material (`mkdocs serve`)

## Development

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -e ".[dev]"
pytest
ruff check src tests
mypy
python -m build
```

## Status

`0.1.0` — pre-1.0. Public API may evolve with SemVer. See `CHANGELOG.md`.

## License

MIT
