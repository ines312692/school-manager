from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.schools.models import School, SchoolDocument
from apps.schools.services import school_name_is_taken


class SchoolSerializer(serializers.ModelSerializer):
    created_by = serializers.SlugRelatedField(slug_field="username", read_only=True)
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = (
            "id",
            "name",
            "address",
            "city",
            "postal_code",
            "student_count",
            "email",
            "phone",
            "website",
            "document_count",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def get_document_count(self, school: School) -> int:
        annotated = getattr(school, "document_count", None)
        return annotated if annotated is not None else school.documents.count()

    def validate(self, attrs: dict) -> dict:
        name = attrs.get("name", getattr(self.instance, "name", ""))
        city = attrs.get("city", getattr(self.instance, "city", ""))
        exclude_pk = self.instance.pk if self.instance else None
        if school_name_is_taken(name, city, exclude_pk=exclude_pk):
            raise serializers.ValidationError(
                {"name": _("Une école portant ce nom existe déjà dans cette ville.")}
            )
        return attrs


class SchoolDocumentSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    uploaded_by = serializers.SlugRelatedField(slug_field="username", read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolDocument
        fields = (
            "id",
            "school",
            "title",
            "file",
            "original_name",
            "content_type",
            "size",
            "uploaded_by",
            "uploaded_at",
            "download_url",
        )
        read_only_fields = ("id", "original_name", "content_type", "size", "uploaded_at")
        extra_kwargs = {"file": {"write_only": True}}

    def get_download_url(self, document: SchoolDocument) -> str:
        path = reverse("schools_api:document-download", kwargs={"pk": document.pk})
        request = self.context.get("request")
        return request.build_absolute_uri(path) if request else path
