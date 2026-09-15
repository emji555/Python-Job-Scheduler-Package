from django.core.management.base import BaseCommand

from workloom.app import get_current_app


class Command(BaseCommand):
    help = "Run Workloom doctor checks"

    def handle(self, *args: object, **options: object) -> None:
        app = get_current_app()
        self.stdout.write(f"backend={app.backend.name}")
        self.stdout.write(f"jobs={', '.join(app.registry.names()) or '(none)'}")
        self.stdout.write(self.style.SUCCESS("OK"))
