from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.testing import make_admin, make_school, make_user
from apps.schools.models import School


class SchoolApiTestCase(APITestCase):
    list_url = reverse("schools_api:school-list")

    def setUp(self) -> None:
        self.admin = make_admin(username="admin")
        self.user = make_user(username="reader")
        self.school = make_school(name="Lycée Victor Hugo", city="Paris", student_count=900)

    def detail_url(self, school: School) -> str:
        return reverse("schools_api:school-detail", kwargs={"pk": school.pk})

    def valid_payload(self, **overrides) -> dict:
        return {
            "name": "Collège Marie Curie",
            "address": "12 avenue des Sciences",
            "city": "Grenoble",
            "postal_code": "38000",
            "student_count": 480,
            "email": "contact@curie.example.com",
            "phone": "+33 4 76 00 00 00",
            "website": "https://curie.example.com",
            **overrides,
        }


class SchoolReadApiTests(SchoolApiTestCase):
    def test_anonymous_user_cannot_list_schools(self) -> None:
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_schools(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Lycée Victor Hugo")
        self.assertEqual(response.data["results"][0]["document_count"], 0)

    def test_authenticated_user_can_retrieve_school(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(self.detail_url(self.school))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_count"], 900)

    def test_list_supports_search_and_ordering(self) -> None:
        make_school(name="École Jules Ferry", city="Marseille", student_count=120)
        make_school(name="Lycée Lumière", city="Lyon", student_count=1500)
        self.client.force_authenticate(self.user)

        search = self.client.get(self.list_url, {"search": "marseille"})
        ordered = self.client.get(self.list_url, {"ordering": "-student_count"})

        self.assertEqual([s["name"] for s in search.data["results"]], ["École Jules Ferry"])
        self.assertEqual(ordered.data["results"][0]["name"], "Lycée Lumière")

    def test_missing_school_returns_404(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse("schools_api:school-detail", kwargs={"pk": 999999}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SchoolCreateApiTests(SchoolApiTestCase):
    def test_admin_can_create_school(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.list_url, self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        school = School.objects.get(pk=response.data["id"])
        self.assertEqual(school.name, "Collège Marie Curie")
        self.assertEqual(school.created_by, self.admin)
        self.assertEqual(response.data["created_by"], "admin")

    def test_regular_user_cannot_create_school(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.post(self.list_url, self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(School.objects.filter(name="Collège Marie Curie").exists())

    def test_create_rejects_duplicate_name_in_same_city(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.list_url, self.valid_payload(name="LYCÉE VICTOR HUGO", city="paris")
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_rejects_invalid_fields(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.list_url,
            self.valid_payload(student_count=-5, email="not-an-email", postal_code="#"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"student_count", "email", "postal_code"})

    def test_create_requires_mandatory_fields(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.list_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue({"name", "address", "city", "postal_code"} <= set(response.data))


class SchoolUpdateApiTests(SchoolApiTestCase):
    def test_admin_can_fully_update_school(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.put(self.detail_url(self.school), self.valid_payload())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.school.refresh_from_db()
        self.assertEqual(self.school.name, "Collège Marie Curie")
        self.assertEqual(self.school.city, "Grenoble")

    def test_admin_can_partially_update_school(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.patch(self.detail_url(self.school), {"student_count": 950})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.school.refresh_from_db()
        self.assertEqual(self.school.student_count, 950)
        self.assertEqual(self.school.name, "Lycée Victor Hugo")

    def test_partial_update_keeping_same_name_is_allowed(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.patch(self.detail_url(self.school), {"name": "Lycée Victor Hugo"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_rejects_name_of_another_school(self) -> None:
        make_school(name="Lycée Condorcet", city="Paris")
        self.client.force_authenticate(self.admin)

        response = self.client.patch(self.detail_url(self.school), {"name": "lycée condorcet"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_regular_user_cannot_update_school(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.patch(self.detail_url(self.school), {"student_count": 1})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.school.refresh_from_db()
        self.assertEqual(self.school.student_count, 900)


class SchoolDeleteApiTests(SchoolApiTestCase):
    def test_admin_can_delete_school(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.delete(self.detail_url(self.school))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(School.objects.filter(pk=self.school.pk).exists())

    def test_regular_user_cannot_delete_school(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.delete(self.detail_url(self.school))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(School.objects.filter(pk=self.school.pk).exists())
