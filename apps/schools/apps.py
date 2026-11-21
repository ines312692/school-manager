from importlib import import_module

from django.apps import AppConfig


class SchoolsConfig(AppConfig):
    name = "apps.schools"
    label = "schools"
    verbose_name = "Écoles"

    def ready(self) -> None:
        import_module(f"{self.name}.signals")
