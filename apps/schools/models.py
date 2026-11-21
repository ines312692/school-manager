import mimetypes
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.schools.validators import validate_document_extension, validate_document_size

postal_code_validator = RegexValidator(
    regex=r"^[0-9A-Za-z][0-9A-Za-z\- ]{1,8}[0-9A-Za-z]$",
    message=_("Code postal invalide."),
)

phone_validator = RegexValidator(
    regex=r"^\+?[0-9 .\-()]{6,20}$",
    message=_("Numéro de téléphone invalide."),
)


class School(TimeStampedModel):
    name = models.CharField(_("nom"), max_length=255)
    address = models.CharField(_("adresse"), max_length=255)
    city = models.CharField(_("ville"), max_length=120)
    postal_code = models.CharField(
        _("code postal"), max_length=10, validators=[postal_code_validator]
    )
    student_count = models.PositiveIntegerField(
        _("nombre d'élèves"), default=0, validators=[MaxValueValidator(100_000)]
    )
    email = models.EmailField(_("e-mail de contact"), blank=True)
    phone = models.CharField(
        _("téléphone"), max_length=20, blank=True, validators=[phone_validator]
    )
    website = models.URLField(_("site web"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("créée par"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_schools",
    )

    class Meta:
        verbose_name = _("école")
        verbose_name_plural = _("écoles")
        ordering = ["name", "city"]
        indexes = [models.Index(fields=["city"], name="schools_city_idx")]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                Lower("city"),
                name="schools_school_name_city_ci_unique",
                violation_error_message=_("Une école portant ce nom existe déjà dans cette ville."),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.city})"

    def get_absolute_url(self) -> str:
        return reverse("schools:detail", kwargs={"pk": self.pk})


def school_document_upload_to(instance: "SchoolDocument", filename: str) -> str:
    extension = Path(filename).suffix.lower()
    return f"schools/{instance.school_id}/documents/{uuid4().hex}{extension}"


class SchoolDocument(models.Model):
    school = models.ForeignKey(
        School, verbose_name=_("école"), on_delete=models.CASCADE, related_name="documents"
    )
    title = models.CharField(_("titre"), max_length=255, blank=True)
    file = models.FileField(
        _("fichier"),
        upload_to=school_document_upload_to,
        max_length=255,
        validators=[validate_document_extension, validate_document_size],
    )
    original_name = models.CharField(_("nom d'origine"), max_length=255, editable=False)
    content_type = models.CharField(_("type MIME"), max_length=100, editable=False)
    size = models.PositiveBigIntegerField(_("taille (octets)"), editable=False)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("déposé par"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    uploaded_at = models.DateTimeField(_("déposé le"), auto_now_add=True)

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        ordering = ["-uploaded_at", "-pk"]

    def __str__(self) -> str:
        return self.title or self.original_name

    def save(self, *args, **kwargs) -> None:
        if self.file and not self.file._committed:
            self._capture_file_metadata()
        if not self.title:
            self.title = Path(self.original_name).stem[:255]
        super().save(*args, **kwargs)

    def _capture_file_metadata(self) -> None:
        original_name = Path(self.file.name).name
        guessed_type, _ = mimetypes.guess_type(original_name)
        self.original_name = original_name[:255]
        self.content_type = guessed_type or "application/octet-stream"
        self.size = self.file.size
