# Jobs

## Decorator

```python
from package_name import job

@job(queue="dhis2", retries=5, timeout=120, backoff="exponential")
def sync_patient(patient_id: int) -> None:
    ...
```

## Canonical dispatch API

Fluent chaining is the canonical style:

```python
sync_patient.dispatch(15).on_queue("dhis2").priority("high").delay(minutes=10)
```

`delay=` may also be passed to `dispatch()` as a `timedelta`. Accessing `.id`, `.status()`, `.result()`, or `.cancel()` on a pending dispatch triggers enqueue.

## Handles

```python
handle = sync_patient.dispatch(15)
handle.id
handle.status()
handle.result()
handle.cancel()  # capability-dependent
```

## Context

```python
from package_name import current_job

@job
def work() -> None:
    print(current_job.id, current_job.attempt, current_job.queue)
```

## Retries

Supports fixed/exponential backoff, jitter, max delay, `retry_on`, and `dont_retry_on`.
