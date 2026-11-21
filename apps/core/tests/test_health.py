from io import StringIO
from unittest import mock

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.url = reverse("health")

    def test_reports_ok_when_database_is_reachable(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})

    def test_reports_service_unavailable_when_database_is_down(self) -> None:
        with mock.patch("apps.core.views.is_database_available", return_value=False):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.json()["database"], "unavailable")


class DatabaseConnectionTests(TestCase):
    def test_database_backend_is_postgresql(self) -> None:
        from django.db import connection

        self.assertEqual(connection.vendor, "postgresql")

    def test_wait_for_db_succeeds_when_database_is_reachable(self) -> None:
        output = StringIO()

        call_command("wait_for_db", timeout=1, stdout=output)

        self.assertIn("disponible", output.getvalue())

    def test_wait_for_db_fails_after_timeout(self) -> None:
        with (
            mock.patch(
                "apps.core.management.commands.wait_for_db.is_database_available",
                return_value=False,
            ),
            self.assertRaises(CommandError),
        ):
            call_command("wait_for_db", timeout=0, interval=0, stdout=StringIO())

    def test_all_migrations_are_applied(self) -> None:
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

        self.assertEqual(plan, [])

    def test_models_have_no_pending_migrations(self) -> None:
        call_command("makemigrations", check=True, dry_run=True, stdout=StringIO())
