import time

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from apps.core.database import is_database_available


class Command(BaseCommand):
    help = "Attend que la base de données soit joignable avant de poursuivre."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--timeout", type=float, default=60.0)
        parser.add_argument("--interval", type=float, default=1.0)
        parser.add_argument("--database", default=DEFAULT_DB_ALIAS)

    def handle(self, *args, timeout: float, interval: float, database: str, **options) -> None:
        deadline = time.monotonic() + timeout
        attempt = 0
        while True:
            attempt += 1
            if is_database_available(database):
                self.stdout.write(self.style.SUCCESS(f"Base de données « {database} » disponible."))
                return
            if time.monotonic() >= deadline:
                raise CommandError(
                    f"Base de données « {database} » injoignable après {attempt} tentative(s)."
                )
            self.stdout.write(f"Base de données indisponible, nouvelle tentative dans {interval}s…")
            time.sleep(interval)
