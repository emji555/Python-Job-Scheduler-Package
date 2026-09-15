# Configuration

## Precedence (highest → lowest)

1. Explicit `App(...)` / `configure(...)` arguments
2. Environment variables (`PACKAGE_*`)
3. Built-in defaults

## Environment variables

```text
PACKAGE_BACKEND=celery
PACKAGE_BROKER_URL=redis://localhost:6379/0
PACKAGE_RESULT_BACKEND=redis://localhost:6379/1
PACKAGE_DEFAULT_QUEUE=default
PACKAGE_TIMEZONE=UTC
PACKAGE_SERIALIZER=json
PACKAGE_STORAGE=memory
PACKAGE_LOCK_BACKEND=redis
PACKAGE_SCHEDULER=inprocess
```

## Explicit app

```python
from package_name import App

app = App(backend="memory", timezone="Africa/Cairo")
app.use()
```
