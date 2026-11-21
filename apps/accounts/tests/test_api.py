from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.core.testing import DEFAULT_PASSWORD, make_user


class RegisterApiTests(APITestCase):
    url = reverse("auth_api:register")

    def payload(self, **overrides) -> dict:
        return {
            "username": "alice",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Martin",
            "password": DEFAULT_PASSWORD,
            "password_confirm": DEFAULT_PASSWORD,
            **overrides,
        }

    def test_registration_creates_user_and_returns_token(self) -> None:
        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="alice")
        self.assertEqual(response.data["user"]["username"], "alice")
        self.assertEqual(response.data["token"], Token.objects.get(user=user).key)
        self.assertNotIn("password", response.data["user"])

    def test_registration_hashes_the_password(self) -> None:
        self.client.post(self.url, self.payload())

        user = User.objects.get(username="alice")
        self.assertNotEqual(user.password, DEFAULT_PASSWORD)
        self.assertTrue(user.check_password(DEFAULT_PASSWORD))

    def test_registration_cannot_self_assign_admin_role(self) -> None:
        response = self.client.post(self.url, self.payload(role=User.Role.ADMIN))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="alice").role, User.Role.USER)

    def test_registration_rejects_duplicate_email_case_insensitively(self) -> None:
        make_user(email="alice@example.com")

        response = self.client.post(self.url, self.payload(email="ALICE@example.com"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_rejects_mismatched_passwords(self) -> None:
        response = self.client.post(self.url, self.payload(password_confirm="Other-Passphrase!"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_registration_rejects_weak_password(self) -> None:
        response = self.client.post(
            self.url, self.payload(password="12345678", password_confirm="12345678")
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(username="alice").exists())


class LoginApiTests(APITestCase):
    url = reverse("auth_api:login")

    def setUp(self) -> None:
        self.user = make_user(username="bob")

    def test_login_with_valid_credentials_returns_token(self) -> None:
        response = self.client.post(self.url, {"username": "bob", "password": DEFAULT_PASSWORD})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], Token.objects.get(user=self.user).key)
        self.assertEqual(response.data["user"]["role"], User.Role.USER)

    def test_login_updates_last_login(self) -> None:
        self.client.post(self.url, {"username": "bob", "password": DEFAULT_PASSWORD})

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_login_with_wrong_password_is_rejected(self) -> None:
        response = self.client.post(self.url, {"username": "bob", "password": "wrong-password"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_login_of_inactive_user_is_rejected(self) -> None:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(self.url, {"username": "bob", "password": DEFAULT_PASSWORD})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutAndMeApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = make_user(username="carol")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_me_returns_the_authenticated_user(self) -> None:
        response = self.client.get(reverse("auth_api:me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "carol")

    def test_logout_revokes_the_token(self) -> None:
        response = self.client.post(reverse("auth_api:logout"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
        self.assertEqual(
            self.client.get(reverse("auth_api:me")).status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_logout_requires_authentication(self) -> None:
        self.client.credentials()

        response = self.client.post(reverse("auth_api:logout"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_is_rejected(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid-token")

        response = self.client.get(reverse("auth_api:me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
