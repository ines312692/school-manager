from django.test import TestCase
from django.urls import reverse

from apps.core.testing import make_user


class OpenApiSchemaTests(TestCase):
    def test_schema_is_generated_and_lists_main_endpoints(self) -> None:
        self.client.force_login(make_user())

        response = self.client.get(reverse("api-schema"), {"format": "json"})

        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        for path in (
            "/api/auth/register/",
            "/api/auth/login/",
            "/api/auth/logout/",
            "/api/schools/",
            "/api/schools/{id}/documents/",
            "/api/documents/{id}/download/",
        ):
            with self.subTest(path=path):
                self.assertIn(path, paths)
