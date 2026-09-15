# Workloom

Laravel-like jobs, queues, scheduling and monitoring for Python — framework and backend agnostic.

```bash
pip install workloom
```

```python
from workloom import job

@job
def send_email(user_id: int) -> None:
    print(user_id)

send_email.dispatch(10)
```

Continue with [Quick start](quickstart.md) and [Architecture](architecture.md).
