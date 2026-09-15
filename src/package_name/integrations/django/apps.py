"""Django AppConfig — configures PACKAGE_NAME from Django settings."""

from __future__ import annotations

from django.apps import AppConfig


class PackageNameConfig(AppConfig):
    name = "package_name.integrations.django"
    label = "package_name"
    verbose_name = "PACKAGE_NAME"

    def ready(self) -> None:
        from django.conf import settings

        from package_name.app import configure

        kwargs = {}
        mapping = {
            "PACKAGE_BACKEND": "backend",
            "PACKAGE_BROKER_URL": "broker_url",
            "PACKAGE_RESULT_BACKEND": "result_backend",
            "PACKAGE_DEFAULT_QUEUE": "default_queue",
            "PACKAGE_TIMEZONE": "timezone",
            "PACKAGE_LOCK_BACKEND": "lock_backend",
            "PACKAGE_STORAGE": "storage",
            "PACKAGE_SCHEDULER": "scheduler",
        }
        for setting_name, key in mapping.items():
            if hasattr(settings, setting_name):
                kwargs[key] = getattr(settings, setting_name)
        if kwargs:
            configure(**kwargs)
