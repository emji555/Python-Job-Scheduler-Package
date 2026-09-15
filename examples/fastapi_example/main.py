"""Minimal FastAPI example."""

from fastapi import FastAPI

from workloom import job
from workloom.integrations.fastapi import create_app

package_app = create_app(backend="eager")
api = FastAPI(title="Workloom FastAPI example")


@job
def send_email(user_id: int) -> str:
    return f"sent:{user_id}"


@api.post("/notify/{user_id}")
def notify(user_id: int) -> dict[str, str]:
    handle = send_email.dispatch(user_id)
    return {"job_id": handle.id, "result": str(handle.result())}


@api.get("/monitor/stats")
def stats() -> dict[str, object]:
    return package_app.monitor.stats()
