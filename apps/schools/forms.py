from django import forms
from django.conf import settings

from apps.schools.models import School, SchoolDocument


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = (
            "name",
            "address",
            "city",
            "postal_code",
            "student_count",
            "email",
            "phone",
            "website",
        )
        widgets = {
            "student_count": forms.NumberInput(attrs={"min": 0}),
        }


class SchoolDocumentForm(forms.ModelForm):
    class Meta:
        model = SchoolDocument
        fields = ("title", "file")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        extensions = ",".join(f".{ext}" for ext in settings.SCHOOL_DOCUMENT_ALLOWED_EXTENSIONS)
        self.fields["file"].widget.attrs["accept"] = extensions
