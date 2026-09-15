# Quick start

```bash
pip install -e ".[dev]"
```

```python
from workloom import configure, job, schedule

configure(backend="eager", timezone="UTC")

@job(retries=3, backoff=1)
def hello(name: str) -> str:
    return f"Hello {name}"

print(hello.dispatch("Eslam").result())

schedule.job(hello).every_five_minutes()
```

## CLI

```bash
workloom doctor
workloom jobs failed
```
