from django.contrib.auth.models import update_last_login
from rest_framework.authtoken.models import Token

from apps.accounts.models import User


def email_is_taken(email: str, *, exclude_pk: int | None = None) -> bool:
    queryset = User.objects.filter(email__iexact=email.strip())
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.exists()


def issue_token(user: User) -> Token:
    token, _ = Token.objects.get_or_create(user=user)
    update_last_login(None, user)
    return token


def revoke_tokens(user: User) -> int:
    deleted, _ = Token.objects.filter(user=user).delete()
    return deleted
