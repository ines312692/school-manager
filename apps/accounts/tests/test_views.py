from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.core.testing import DEFAULT_PASSWORD, make_user


class SignUpViewTests(TestCase):
    url = reverse("accounts:signup")

    def test_signup_page_is_rendered(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_signup_creates_regular_user_and_logs_in(self) -> None:
        response = self.client.post(
            self.url,
            {
                "username": "dave",
                "email": "Dave@Example.com",
                "first_name": "Dave",
                "last_name": "Durand",
                "password1": DEFAULT_PASSWORD,
                "password2": DEFAULT_PASSWORD,
            },
        )

        self.assertRedirects(response, reverse("schools:list"))
        user = User.objects.get(username="dave")
        self.assertEqual(user.email, "dave@example.com")
        self.assertEqual(user.role, User.Role.USER)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_signup_rejects_duplicate_email(self) -> None:
        make_user(email="dave@example.com")

        response = self.client.post(
            self.url,
            {
                "username": "dave",
                "email": "DAVE@example.com",
                "password1": DEFAULT_PASSWORD,
                "password2": DEFAULT_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "Un compte utilise déjà cette adresse e-mail."
        )

    def test_authenticated_user_is_redirected_away_from_signup(self) -> None:
        self.client.force_login(make_user())

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("schools:list"))


class LoginLogoutViewTests(TestCase):
    def setUp(self) -> None:
        self.user = make_user(username="erin")

    def test_login_with_valid_credentials(self) -> None:
        response = self.client.post(
            reverse("accounts:login"), {"username": "erin", "password": DEFAULT_PASSWORD}
        )

        self.assertRedirects(response, reverse("schools:list"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_with_invalid_credentials(self) -> None:
        response = self.client.post(
            reverse("accounts:login"), {"username": "erin", "password": "nope"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_the_session(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
