# Configuration

## Precedence (highest → lowest)

1. Explicit `App(...)` / `configure(...)` arguments
2. Environment variables (`WORKLOOM_*`)
3. Built-in defaults

## Environment variables

```text
WORKLOOM_BACKEND=celery
WORKLOOM_BROKER_URL=redis://localhost:6379/0
WORKLOOM_RESULT_BACKEND=redis://localhost:6379/1
WORKLOOM_DEFAULT_QUEUE=default
WORKLOOM_TIMEZONE=UTC
WORKLOOM_SERIALIZER=json
WORKLOOM_STORAGE=memory
WORKLOOM_LOCK_BACKEND=redis
WORKLOOM_SCHEDULER=inprocess
```

## Explicit app

```python
from workloom import App

app = App(backend="memory", timezone="Africa/Cairo")
app.use()
```
