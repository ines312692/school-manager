import itertools
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from apps.accounts.models import User
from apps.schools.models import School

DEFAULT_PASSWORD = "Str0ng-Passphrase!"

_sequence = itertools.count(1)


def make_user(*, role: str = User.Role.USER, password: str = DEFAULT_PASSWORD, **fields) -> User:
    index = next(_sequence)
    fields.setdefault("username", f"user{index}")
    fields.setdefault("email", f"user{index}@example.com")
    return User.objects.create_user(role=role, password=password, **fields)


def make_admin(**fields) -> User:
    return make_user(role=User.Role.ADMIN, **fields)


def make_school(**fields) -> School:
    index = next(_sequence)
    defaults = {
        "name": f"École {index}",
        "address": f"{index} rue de la République",
        "city": "Lyon",
        "postal_code": "69001",
        "student_count": 250,
    }
    return School.objects.create(**{**defaults, **fields})


def make_upload(
    name: str = "rapport.pdf",
    content: bytes = b"%PDF-1.4 school-manager",
    content_type: str = "application/pdf",
) -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content, content_type=content_type)


class TemporaryMediaRootMixin:
    @classmethod
    def setUpClass(cls) -> None:
        cls._media_root = tempfile.mkdtemp(prefix="school-manager-tests-")
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_root)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_root, ignore_errors=True)
