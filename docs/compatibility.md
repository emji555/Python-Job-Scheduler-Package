# Compatibility matrix

Only mark features supported after tests cover them.

| | Eager | Memory | Celery | RQ | Dramatiq |
| --- | --- | --- | --- | --- | --- |
| Immediate jobs | ✓ | ✓ | ✓ | planned | planned |
| Delayed jobs | — | ✓ | ✓ | ? | ? |
| Results | ✓ | ✓ | ✓ | ? | ? |
| Retries | ✓ | ✓ | ✓ | ? | ? |
| Priorities | — | ✓ | ✓ | ? | ? |
| Cancellation | — | ✓ | ✓ | ? | ? |
| Async jobs | ✓ | ✓ | — | ? | ? |
