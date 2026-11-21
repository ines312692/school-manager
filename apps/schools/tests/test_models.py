from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.core.testing import make_school
from apps.schools.models import School


class SchoolModelTests(TestCase):
    def test_string_representation(self) -> None:
        school = make_school(name="Lycée Ampère", city="Lyon")

        self.assertEqual(str(school), "Lycée Ampère (Lyon)")

    def test_absolute_url_points_to_detail_page(self) -> None:
        school = make_school()

        self.assertEqual(school.get_absolute_url(), f"/schools/{school.pk}/")

    def test_name_and_city_are_unique_case_insensitively_in_database(self) -> None:
        make_school(name="Collège Jean Moulin", city="Paris")

        with self.assertRaises(IntegrityError), transaction.atomic():
            make_school(name="collège jean moulin", city="PARIS")

    def test_same_name_is_allowed_in_another_city(self) -> None:
        make_school(name="Collège Jean Moulin", city="Paris")

        make_school(name="Collège Jean Moulin", city="Lyon")

        self.assertEqual(School.objects.filter(name="Collège Jean Moulin").count(), 2)

    def test_full_clean_reports_duplicate_school(self) -> None:
        make_school(name="École Pasteur", city="Lille")
        duplicate = School(
            name="ÉCOLE PASTEUR", address="1 rue X", city="lille", postal_code="59000"
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_full_clean_rejects_invalid_values(self) -> None:
        school = School(
            name="École", address="1 rue X", city="Lille", postal_code="!", student_count=200_000
        )

        with self.assertRaises(ValidationError) as context:
            school.full_clean()

        self.assertIn("postal_code", context.exception.message_dict)
        self.assertIn("student_count", context.exception.message_dict)
