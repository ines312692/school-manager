from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from apps.accounts.managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", _("Administrateur")
        USER = "user", _("Utilisateur")

    email = models.EmailField(_("adresse e-mail"))
    role = models.CharField(
        _("rôle"),
        max_length=16,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )

    objects = UserManager()

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        ordering = ["username"]
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
                violation_error_message=_("Un compte utilise déjà cette adresse e-mail."),
            ),
        ]

    def clean(self) -> None:
        super().clean()
        self.email = self.email.strip().lower()

    def save(self, *args, **kwargs) -> None:
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def is_admin(self) -> bool:
        return self.is_active and (self.is_superuser or self.role == self.Role.ADMIN)
