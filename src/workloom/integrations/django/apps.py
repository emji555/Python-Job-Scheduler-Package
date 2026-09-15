"""Django AppConfig — configures Workloom from Django settings."""

from __future__ import annotations

from django.apps import AppConfig


class WorkloomConfig(AppConfig):
    name = "workloom.integrations.django"
    label = "workloom"
    verbose_name = "Workloom"

    def ready(self) -> None:
        from django.conf import settings

        from workloom.app import configure

        kwargs = {}
        mapping = {
            "WORKLOOM_BACKEND": "backend",
            "WORKLOOM_BROKER_URL": "broker_url",
            "WORKLOOM_RESULT_BACKEND": "result_backend",
            "WORKLOOM_DEFAULT_QUEUE": "default_queue",
            "WORKLOOM_TIMEZONE": "timezone",
            "WORKLOOM_LOCK_BACKEND": "lock_backend",
            "WORKLOOM_STORAGE": "storage",
            "WORKLOOM_SCHEDULER": "scheduler",
        }
        for setting_name, key in mapping.items():
            if hasattr(settings, setting_name):
                kwargs[key] = getattr(settings, setting_name)
        if kwargs:
            configure(**kwargs)
