import apps.schools.models
import apps.schools.validators
import django.core.validators
import django.db.models.deletion
import django.db.models.functions.text
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="créé le"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="mis à jour le"),
                ),
                ("name", models.CharField(max_length=255, verbose_name="nom")),
                ("address", models.CharField(max_length=255, verbose_name="adresse")),
                ("city", models.CharField(max_length=120, verbose_name="ville")),
                (
                    "postal_code",
                    models.CharField(
                        max_length=10,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Code postal invalide.",
                                regex="^[0-9A-Za-z][0-9A-Za-z\\- ]{1,8}[0-9A-Za-z]$",
                            )
                        ],
                        verbose_name="code postal",
                    ),
                ),
                (
                    "student_count",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(100000)],
                        verbose_name="nombre d'élèves",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="e-mail de contact"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Numéro de téléphone invalide.",
                                regex="^\\+?[0-9 .\\-()]{6,20}$",
                            )
                        ],
                        verbose_name="téléphone",
                    ),
                ),
                ("website", models.URLField(blank=True, verbose_name="site web")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_schools",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="créée par",
                    ),
                ),
            ],
            options={
                "verbose_name": "école",
                "verbose_name_plural": "écoles",
                "ordering": ["name", "city"],
            },
        ),
        migrations.CreateModel(
            name="SchoolDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(blank=True, max_length=255, verbose_name="titre"),
                ),
                (
                    "file",
                    models.FileField(
                        max_length=255,
                        upload_to=apps.schools.models.school_document_upload_to,
                        validators=[
                            apps.schools.validators.DocumentExtensionValidator(),
                            apps.schools.validators.DocumentSizeValidator(),
                        ],
                        verbose_name="fichier",
                    ),
                ),
                (
                    "original_name",
                    models.CharField(
                        editable=False, max_length=255, verbose_name="nom d'origine"
                    ),
                ),
                (
                    "content_type",
                    models.CharField(
                        editable=False, max_length=100, verbose_name="type MIME"
                    ),
                ),
                (
                    "size",
                    models.PositiveBigIntegerField(
                        editable=False, verbose_name="taille (octets)"
                    ),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="déposé le"),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="schools.school",
                        verbose_name="école",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="déposé par",
                    ),
                ),
            ],
            options={
                "verbose_name": "document",
                "verbose_name_plural": "documents",
                "ordering": ["-uploaded_at", "-pk"],
            },
        ),
        migrations.AddIndex(
            model_name="school",
            index=models.Index(fields=["city"], name="schools_city_idx"),
        ),
        migrations.AddConstraint(
            model_name="school",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("name"),
                django.db.models.functions.text.Lower("city"),
                name="schools_school_name_city_ci_unique",
                violation_error_message="Une école portant ce nom existe déjà dans cette ville.",
            ),
        ),
    ]
