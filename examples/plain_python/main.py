"""Plain Python quickstart example."""

from workloom import configure, job

configure(backend="eager")


@job
def add(a: int, b: int) -> int:
    return a + b


@job(queue="dhis2", retries=5, backoff="exponential")
def sync_patient(patient_id: int) -> dict[str, int]:
    # Example only — no healthcare business logic in the library itself.
    return {"patient_id": patient_id, "synced": 1}


if __name__ == "__main__":
    print(add.dispatch(2, 40).result())
    print(sync_patient.dispatch(15).result())
