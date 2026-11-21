from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.testing import (
    TemporaryMediaRootMixin,
    make_admin,
    make_school,
    make_upload,
    make_user,
)
from apps.schools.models import SchoolDocument


def stored_path(document: SchoolDocument) -> Path:
    return Path(settings.MEDIA_ROOT) / document.file.name


class SchoolDocumentModelTests(TemporaryMediaRootMixin, TestCase):
    def setUp(self) -> None:
        self.school = make_school()

    def test_metadata_is_captured_on_upload(self) -> None:
        document = SchoolDocument.objects.create(
            school=self.school, file=make_upload("Bilan Annuel.pdf", b"%PDF-1.4 data")
        )

        self.assertEqual(document.original_name, "Bilan Annuel.pdf")
        self.assertEqual(document.content_type, "application/pdf")
        self.assertEqual(document.size, len(b"%PDF-1.4 data"))
        self.assertEqual(document.title, "Bilan Annuel")

    def test_file_is_stored_under_an_unguessable_name(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload("a.pdf"))

        self.assertTrue(document.file.name.startswith(f"schools/{self.school.pk}/documents/"))
        self.assertNotIn("a.pdf", document.file.name)
        self.assertTrue(stored_path(document).is_file())

    def test_file_is_removed_from_storage_when_document_is_deleted(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())
        path = stored_path(document)

        with self.captureOnCommitCallbacks(execute=True):
            document.delete()

        self.assertFalse(path.exists())

    def test_files_are_removed_when_school_is_deleted(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())
        path = stored_path(document)

        with self.captureOnCommitCallbacks(execute=True):
            self.school.delete()

        self.assertFalse(path.exists())

    def test_previous_file_is_removed_when_file_is_replaced(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload("v1.pdf"))
        previous_path = stored_path(document)

        with self.captureOnCommitCallbacks(execute=True):
            document.file = make_upload("v2.pdf", b"%PDF-1.4 v2")
            document.save()

        self.assertFalse(previous_path.exists())
        self.assertTrue(stored_path(document).is_file())
        self.assertEqual(document.original_name, "v2.pdf")


class SchoolDocumentApiTests(TemporaryMediaRootMixin, APITestCase):
    def setUp(self) -> None:
        self.admin = make_admin()
        self.user = make_user()
        self.school = make_school()
        self.upload_url = reverse("schools_api:school-documents", kwargs={"pk": self.school.pk})

    def test_admin_can_upload_document(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.upload_url,
            {"title": "Projet d'établissement", "file": make_upload("projet.pdf")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        document = SchoolDocument.objects.get(pk=response.data["id"])
        self.assertEqual(document.school, self.school)
        self.assertEqual(document.uploaded_by, self.admin)
        self.assertEqual(response.data["original_name"], "projet.pdf")
        self.assertNotIn("file", response.data)
        self.assertTrue(
            response.data["download_url"].endswith(f"/api/documents/{document.pk}/download/")
        )
        self.assertTrue(stored_path(document).is_file())

    def test_regular_user_cannot_upload_document(self) -> None:
        self.client.force_authenticate(self.user)

        response = self.client.post(self.upload_url, {"file": make_upload()}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(SchoolDocument.objects.exists())

    def test_upload_requires_a_file(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(self.upload_url, {"title": "Vide"}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_upload_rejects_forbidden_extension(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.upload_url,
            {"file": make_upload("script.exe", b"MZ", "application/octet-stream")},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)
        self.assertFalse(SchoolDocument.objects.exists())

    @override_settings(SCHOOL_DOCUMENT_MAX_SIZE=10)
    def test_upload_rejects_file_exceeding_max_size(self) -> None:
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.upload_url, {"file": make_upload(content=b"x" * 11)}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_user_can_list_documents_of_a_school(self) -> None:
        SchoolDocument.objects.create(school=self.school, file=make_upload("a.pdf"))
        SchoolDocument.objects.create(school=make_school(), file=make_upload("b.pdf"))
        self.client.force_authenticate(self.user)

        nested = self.client.get(self.upload_url)
        filtered = self.client.get(reverse("schools_api:document-list"), {"school": self.school.pk})

        self.assertEqual(nested.status_code, status.HTTP_200_OK)
        self.assertEqual(nested.data["count"], 1)
        self.assertEqual(filtered.data["count"], 1)
        self.assertEqual(filtered.data["results"][0]["original_name"], "a.pdf")

    def test_invalid_school_filter_returns_empty_list(self) -> None:
        SchoolDocument.objects.create(school=self.school, file=make_upload())
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse("schools_api:document-list"), {"school": "abc"})

        self.assertEqual(response.data["count"], 0)

    def test_user_can_download_document_as_attachment(self) -> None:
        document = SchoolDocument.objects.create(
            school=self.school, file=make_upload("note.txt", b"bonjour", "text/plain")
        )
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse("schools_api:document-download", kwargs={"pk": document.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(b"".join(response.streaming_content), b"bonjour")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("note.txt", response["Content-Disposition"])

    def test_download_of_missing_file_returns_404(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())
        stored_path(document).unlink()
        self.client.force_authenticate(self.user)

        response = self.client.get(
            reverse("schools_api:document-download", kwargs={"pk": document.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_download_document(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())

        response = self.client.get(
            reverse("schools_api:document-download", kwargs={"pk": document.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_delete_document(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())
        path = stored_path(document)
        self.client.force_authenticate(self.admin)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(
                reverse("schools_api:document-detail", kwargs={"pk": document.pk})
            )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SchoolDocument.objects.exists())
        self.assertFalse(path.exists())

    def test_regular_user_cannot_delete_document(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())
        self.client.force_authenticate(self.user)

        response = self.client.delete(
            reverse("schools_api:document-detail", kwargs={"pk": document.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(SchoolDocument.objects.filter(pk=document.pk).exists())


class SchoolDocumentPageTests(TemporaryMediaRootMixin, TestCase):
    def setUp(self) -> None:
        self.admin = make_admin()
        self.user = make_user()
        self.school = make_school()
        self.upload_url = reverse("schools:document-upload", args=[self.school.pk])

    def test_admin_sees_upload_form_on_detail_page(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.get(self.school.get_absolute_url())

        self.assertIn("document_form", response.context)
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_admin_can_upload_document_from_page(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            self.upload_url, {"title": "Règlement intérieur", "file": make_upload("reglement.pdf")}
        )

        self.assertRedirects(response, self.school.get_absolute_url())
        document = SchoolDocument.objects.get()
        self.assertEqual(document.title, "Règlement intérieur")
        self.assertEqual(document.uploaded_by, self.admin)

    def test_invalid_upload_is_redisplayed(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            self.upload_url, {"file": make_upload("virus.sh", b"#!/bin/sh", "text/x-sh")}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schools/document_form.html")
        self.assertIn("file", response.context["form"].errors)

    def test_regular_user_cannot_upload_from_page(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(self.upload_url, {"file": make_upload()})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(SchoolDocument.objects.exists())

    def test_upload_to_unknown_school_returns_404(self) -> None:
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("schools:document-upload", args=[999999]), {"file": make_upload()}
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_download_document_from_page(self) -> None:
        document = SchoolDocument.objects.create(
            school=self.school, file=make_upload("liste.csv", b"a,b\n1,2\n", "text/csv")
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("schools:document-download", args=[document.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"a,b\n1,2\n")

    def test_admin_can_delete_document_from_page(self) -> None:
        document = SchoolDocument.objects.create(school=self.school, file=make_upload())
        self.client.force_login(self.admin)

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse("schools:document-delete", args=[document.pk]))

        self.assertRedirects(response, self.school.get_absolute_url())
        self.assertFalse(SchoolDocument.objects.exists())
