# PACKAGE_NAME

Laravel-inspired **jobs, queues, scheduling, retries, locks, failed jobs, pipelines, and monitoring** for the Python ecosystem — without coupling your application to Django, FastAPI, Flask, Celery, or any single task engine.

> Temporary names (rename before first PyPI release):
> - Distribution: `package-name`
> - Import: `package_name`
> - CLI: `package-name`
> - Env prefix: `PACKAGE_`

## Install

```bash
pip install package-name
```

Optional extras:

```bash
pip install "package-name[celery]"
pip install "package-name[redis]"
pip install "package-name[django]"
pip install "package-name[fastapi]"
pip install "package-name[flask]"
```

## Quick start

```python
from package_name import job

@job
def send_email(user_id: int) -> None:
    print(user_id)

send_email.dispatch(10)
```

## Production-shaped example

```python
from package_name import configure, job, schedule

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

Python teams often hard-wire Celery or Django-Q into domain code. `PACKAGE_NAME` gives you a stable Laravel-like API and a plugin architecture around proven engines — not a new broker.

See [docs/architecture.md](docs/architecture.md).

## CLI

```bash
package-name doctor
package-name worker
package-name schedule run
package-name schedule list
package-name queues
package-name jobs failed
package-name jobs retry --all
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
