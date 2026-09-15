# Backends

| Capability | Eager | Memory | Celery |
| --- | --- | --- | --- |
| Immediate jobs | ✓ | ✓ | ✓ |
| Delayed jobs | — | ✓ | ✓ |
| Results | ✓ | ✓ | ✓ |
| Retries | ✓ | ✓ | ✓ |
| Priorities | — | ✓ | ✓ |
| Cancellation | — | ✓ | ✓ |
| Async jobs | ✓ | ✓ | — |
| Chains/groups (emulated) | ✓ | ✓ | — |

Unsupported features raise `UnsupportedCapabilityError`.

## Celery

```bash
pip install "workloom[celery]"
```

```python
configure(backend="celery", broker_url="redis://localhost:6379/0")
```

Workers still run via Celery's own worker process; this package provides the application-facing API and envelope execution task.
