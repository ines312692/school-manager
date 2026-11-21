from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class DocumentExtensionValidator:
    def __call__(self, file: File) -> None:
        FileExtensionValidator(allowed_extensions=settings.SCHOOL_DOCUMENT_ALLOWED_EXTENSIONS)(file)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DocumentExtensionValidator)


@deconstructible
class DocumentSizeValidator:
    def __call__(self, file: File) -> None:
        limit = settings.SCHOOL_DOCUMENT_MAX_SIZE
        if file.size > limit:
            raise ValidationError(
                _("Le fichier dépasse la taille maximale autorisée (%(limit)s)."),
                code="file_too_large",
                params={"limit": filesizeformat(limit)},
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DocumentSizeValidator)


validate_document_extension = DocumentExtensionValidator()
validate_document_size = DocumentSizeValidator()
