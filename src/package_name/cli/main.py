"""CLI entrypoint: package-name ..."""

from __future__ import annotations

import json
import sys
from typing import Any

import click

from package_name import __version__
from package_name.app import configure, get_current_app
from package_name.core.redaction import redact_mapping
from package_name.plugins import (
    GROUP_BACKENDS,
    GROUP_LOCKS,
    GROUP_SCHEDULERS,
    GROUP_SERIALIZERS,
    GROUP_STORAGE,
    list_plugins,
)


@click.group()
@click.version_option(__version__, prog_name="package-name")
def main() -> None:
    """PACKAGE_NAME — jobs, queues, scheduling, and monitoring."""


@main.command("worker")
@click.option("--backend", default=None, help="Backend plugin name")
@click.option("--queues", default="default", help="Comma-separated queue names")
def worker_cmd(backend: str | None, queues: str) -> None:
    """Run a worker loop for backends that support local processing."""
    overrides: dict[str, Any] = {}
    if backend:
        overrides["backend"] = backend
    app = configure(**overrides)
    click.echo(f"Worker starting backend={app.backend.name} queues={queues}")
    if hasattr(app.backend, "start_worker"):
        app.backend.start_worker()  # type: ignore[attr-defined]
        click.echo("Memory worker running. Press Ctrl+C to stop.")
        try:
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            if hasattr(app.backend, "stop_worker"):
                app.backend.stop_worker()  # type: ignore[attr-defined]
            click.echo("Stopped.")
    elif app.backend.name == "celery":
        click.echo(
            "For Celery, run the Celery worker separately, e.g.\n"
            "  celery -A your_app worker -l info"
        )
    else:
        click.echo(f"Backend {app.backend.name!r} has no local worker loop.")


@main.group("schedule")
def schedule_group() -> None:
    """Scheduler commands."""


@schedule_group.command("run")
def schedule_run() -> None:
    """Run the in-process scheduler until interrupted."""
    app = get_current_app()
    click.echo(f"Scheduler starting ({app.scheduler_backend.name})")
    app.scheduler_backend.start()
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        app.scheduler_backend.stop()
        click.echo("Scheduler stopped.")


@schedule_group.command("list")
def schedule_list() -> None:
    app = get_current_app()
    for entry in app.scheduler_backend.list():
        click.echo(
            f"{entry.id} job={entry.job_name} cron={entry.cron!r} tz={entry.timezone} "
            f"overlap={entry.without_overlapping} one_server={entry.on_one_server}"
        )


@main.command("queues")
def queues_cmd() -> None:
    app = get_current_app()
    for q in app.monitor.queues():
        click.echo(json.dumps(q))


@main.group("jobs")
def jobs_group() -> None:
    """Failed job management."""


@jobs_group.command("failed")
def jobs_failed() -> None:
    app = get_current_app()
    for record in app.failed_jobs.list():
        safe = redact_mapping(record.to_dict(), app.settings.redact_keys)
        # Never dump full tracebacks with potential secrets in default CLI view
        safe.pop("traceback", None)
        click.echo(json.dumps(safe, default=str))


@jobs_group.command("retry")
@click.argument("failed_id", required=False)
@click.option("--all", "retry_all", is_flag=True)
def jobs_retry(failed_id: str | None, retry_all: bool) -> None:
    app = get_current_app()
    if retry_all:
        handles = app.failed_jobs.retry_all()
        click.echo(f"Retried {len(handles)} failed job(s)")
        return
    if not failed_id:
        raise click.UsageError("Provide FAILED_ID or --all")
    handle = app.failed_jobs.retry(failed_id)
    click.echo(f"Retried as {handle.id}")


@jobs_group.command("delete")
@click.argument("failed_id")
def jobs_delete(failed_id: str) -> None:
    app = get_current_app()
    ok = app.failed_jobs.delete(failed_id)
    click.echo("deleted" if ok else "not found")


@main.command("doctor")
def doctor_cmd() -> None:
    """Inspect configuration and common problems."""
    app = get_current_app()
    checks: list[tuple[str, bool, str]] = []

    checks.append(("configuration", True, f"backend={app.settings.backend}"))
    checks.append(
        (
            "backend plugin",
            app.settings.backend in list_plugins(GROUP_BACKENDS),
            app.settings.backend,
        )
    )
    checks.append(
        (
            "serializer plugin",
            app.settings.serializer in list_plugins(GROUP_SERIALIZERS),
            app.settings.serializer,
        )
    )
    checks.append(
        (
            "storage plugin",
            app.settings.storage in list_plugins(GROUP_STORAGE),
            app.settings.storage,
        )
    )
    checks.append(
        (
            "lock plugin",
            app.settings.lock_backend in list_plugins(GROUP_LOCKS),
            app.settings.lock_backend,
        )
    )
    checks.append(
        (
            "scheduler plugin",
            app.settings.scheduler in list_plugins(GROUP_SCHEDULERS),
            app.settings.scheduler,
        )
    )

    # Optional reachability
    if app.settings.lock_backend == "redis" or app.settings.backend == "celery":
        url = app.settings.broker_url
        if not url:
            checks.append(("broker_url", False, "PACKAGE_BROKER_URL not set"))
        else:
            try:
                import redis

                client = redis.Redis.from_url(url)
                client.ping()
                checks.append(("broker reachable", True, url))
            except Exception as exc:
                checks.append(("broker reachable", False, str(exc)))
    else:
        checks.append(("broker reachable", True, "not required for current backend"))

    checks.append(("storage reachable", True, app.storage.name))
    checks.append(("lock backend reachable", True, app.lock_backend.name))
    checks.append(("scheduler available", True, app.scheduler_backend.name))

    failed = False
    for name, ok, detail in checks:
        status = "OK" if ok else "FAIL"
        if not ok:
            failed = True
        click.echo(f"[{status}] {name}: {detail}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
