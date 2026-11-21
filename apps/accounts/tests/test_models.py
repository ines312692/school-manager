from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.accounts.models import User
from apps.core.testing import DEFAULT_PASSWORD, make_user


class UserModelTests(TestCase):
    def test_new_user_has_regular_role_by_default(self) -> None:
        user = make_user()

        self.assertEqual(user.role, User.Role.USER)
        self.assertFalse(user.is_admin)

    def test_superuser_is_created_with_admin_role(self) -> None:
        user = User.objects.create_superuser("root", "root@example.com", DEFAULT_PASSWORD)

        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_admin)

    def test_admin_role_grants_admin_rights(self) -> None:
        user = make_user(role=User.Role.ADMIN)

        self.assertTrue(user.is_admin)

    def test_inactive_admin_has_no_admin_rights(self) -> None:
        user = make_user(role=User.Role.ADMIN, is_active=False)

        self.assertFalse(user.is_admin)

    def test_password_is_never_stored_in_clear_text(self) -> None:
        user = make_user(password=DEFAULT_PASSWORD)

        self.assertNotEqual(user.password, DEFAULT_PASSWORD)
        self.assertTrue(user.check_password(DEFAULT_PASSWORD))

    @override_settings(
        PASSWORD_HASHERS=[
            "django.contrib.auth.hashers.Argon2PasswordHasher",
            "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        ]
    )
    def test_password_is_hashed_with_argon2(self) -> None:
        user = make_user(password=DEFAULT_PASSWORD)

        self.assertEqual(identify_hasher(user.password).algorithm, "argon2")

    def test_email_is_normalized_to_lowercase(self) -> None:
        user = make_user(email="Jane.DOE@Example.COM")

        self.assertEqual(user.email, "jane.doe@example.com")

    def test_email_uniqueness_is_case_insensitive(self) -> None:
        make_user(email="jane@example.com")
        duplicate = User(username="jane2", email="JANE@example.com")
        duplicate.set_password(DEFAULT_PASSWORD)

        with self.assertRaises(ValidationError):
            duplicate.full_clean()
