from django.test import TestCase
from django.urls import reverse

from apps.core.testing import make_admin, make_school, make_user
from apps.schools.models import School


class SchoolPagesTestCase(TestCase):
    def setUp(self) -> None:
        self.admin = make_admin()
        self.user = make_user()
        self.school = make_school(name="École Montessori", city="Nantes")

    def form_data(self, **overrides) -> dict:
        return {
            "name": "École Saint-Exupéry",
            "address": "3 place du Ciel",
            "city": "Toulouse",
            "postal_code": "31000",
            "student_count": 320,
            "email": "",
            "phone": "",
            "website": "",
            **overrides,
        }


class SchoolListPageTests(SchoolPagesTestCase):
    url = reverse("schools:list")

    def test_anonymous_user_is_redirected_to_login(self) -> None:
        response = self.client.get(self.url)

        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.url}")

    def test_authenticated_user_sees_available_schools(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "École Montessori")
        self.assertNotContains(response, reverse("schools:create"))

    def test_admin_sees_management_actions(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.get(self.url)

        self.assertContains(response, reverse("schools:create"))
        self.assertContains(response, reverse("schools:update", args=[self.school.pk]))

    def test_list_can_be_filtered(self) -> None:
        make_school(name="Lycée Descartes", city="Tours")
        self.client.force_login(self.user)

        response = self.client.get(self.url, {"q": "tours"})

        self.assertContains(response, "Lycée Descartes")
        self.assertNotContains(response, "École Montessori")

    def test_detail_page_is_accessible(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(self.school.get_absolute_url())

        self.assertContains(response, "École Montessori")
        self.assertNotIn("document_form", response.context)


class SchoolCreatePageTests(SchoolPagesTestCase):
    url = reverse("schools:create")

    def test_admin_can_create_school(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(self.url, self.form_data())

        school = School.objects.get(name="École Saint-Exupéry")
        self.assertRedirects(response, school.get_absolute_url())
        self.assertEqual(school.created_by, self.admin)

    def test_invalid_form_is_redisplayed_with_errors(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(self.url, self.form_data(name="", student_count=-1))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(School.objects.filter(city="Toulouse").exists())

    def test_duplicate_school_is_rejected(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            self.url, self.form_data(name="école montessori", city="NANTES")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(School.objects.filter(city__iexact="nantes").count(), 1)

    def test_regular_user_is_forbidden(self) -> None:
        self.client.force_login(self.user)

        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, self.form_data()).status_code, 403)
        self.assertFalse(School.objects.filter(city="Toulouse").exists())


class SchoolUpdateDeletePageTests(SchoolPagesTestCase):
    def test_admin_can_update_school(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("schools:update", args=[self.school.pk]),
            self.form_data(name="École Montessori", city="Nantes", student_count=410),
        )

        self.assertRedirects(response, self.school.get_absolute_url())
        self.school.refresh_from_db()
        self.assertEqual(self.school.student_count, 410)

    def test_regular_user_cannot_update_school(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("schools:update", args=[self.school.pk]), self.form_data()
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_school(self) -> None:
        self.client.force_login(self.admin)
        url = reverse("schools:delete", args=[self.school.pk])

        confirmation = self.client.get(url)
        response = self.client.post(url)

        self.assertContains(confirmation, "Supprimer définitivement")
        self.assertRedirects(response, reverse("schools:list"))
        self.assertFalse(School.objects.filter(pk=self.school.pk).exists())

    def test_regular_user_cannot_delete_school(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(reverse("schools:delete", args=[self.school.pk]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(School.objects.filter(pk=self.school.pk).exists())
