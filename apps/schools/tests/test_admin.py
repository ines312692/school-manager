from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.core.testing import TemporaryMediaRootMixin, make_school, make_upload
from apps.schools.models import School, SchoolDocument


class SchoolAdminTests(TemporaryMediaRootMixin, TestCase):
    def setUp(self) -> None:
        self.superuser = User.objects.create_superuser("root", "root@example.com", "Str0ng-Pass!")
        self.client.force_login(self.superuser)

    def inline_management_data(self, total: int = 0, initial: int = 0) -> dict:
        return {
            "documents-TOTAL_FORMS": str(total),
            "documents-INITIAL_FORMS": str(initial),
            "documents-MIN_NUM_FORMS": "0",
            "documents-MAX_NUM_FORMS": "1000",
        }

    def test_school_created_in_admin_records_creator_and_inline_document(self) -> None:
        response = self.client.post(
            reverse("admin:schools_school_add"),
            {
                "name": "Lycée Admin",
                "address": "1 rue Centrale",
                "city": "Dijon",
                "postal_code": "21000",
                "student_count": "100",
                **self.inline_management_data(total=1),
                "documents-0-title": "Charte",
                "documents-0-file": make_upload("charte.pdf"),
            },
        )

        self.assertEqual(response.status_code, 302)
        school = School.objects.get(name="Lycée Admin")
        self.assertEqual(school.created_by, self.superuser)
        self.assertEqual(school.documents.get().uploaded_by, self.superuser)

    def test_inline_document_can_be_deleted_from_admin(self) -> None:
        school = make_school()
        document = SchoolDocument.objects.create(school=school, file=make_upload())

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse("admin:schools_school_change", args=[school.pk]),
                {
                    "name": school.name,
                    "address": school.address,
                    "city": school.city,
                    "postal_code": school.postal_code,
                    "student_count": school.student_count,
                    **self.inline_management_data(total=1, initial=1),
                    "documents-0-id": document.pk,
                    "documents-0-school": school.pk,
                    "documents-0-title": document.title,
                    "documents-0-DELETE": "on",
                },
            )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SchoolDocument.objects.exists())

    def test_document_uploaded_from_document_admin_records_uploader(self) -> None:
        school = make_school()

        response = self.client.post(
            reverse("admin:schools_schooldocument_add"),
            {"school": school.pk, "title": "", "file": make_upload("budget.xlsx", b"xlsx")},
        )

        self.assertEqual(response.status_code, 302)
        document = SchoolDocument.objects.get()
        self.assertEqual(document.uploaded_by, self.superuser)
        self.assertEqual(document.title, "budget")

    def test_admin_changelists_are_reachable(self) -> None:
        for name in (
            "admin:schools_school_changelist",
            "admin:schools_schooldocument_changelist",
            "admin:accounts_user_changelist",
        ):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
