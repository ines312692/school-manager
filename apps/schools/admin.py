from django.contrib import admin

from apps.schools.models import School, SchoolDocument


class SchoolDocumentInline(admin.TabularInline):
    model = SchoolDocument
    extra = 0
    fields = ("title", "file", "original_name", "content_type", "size", "uploaded_at")
    readonly_fields = ("original_name", "content_type", "size", "uploaded_at")


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "postal_code", "student_count", "created_at")
    list_filter = ("city",)
    search_fields = ("name", "city", "postal_code", "address")
    readonly_fields = ("created_by", "created_at", "updated_at")
    inlines = [SchoolDocumentInline]

    def save_model(self, request, obj, form, change) -> None:
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change) -> None:
        for document in formset.save(commit=False):
            if document.uploaded_by_id is None:
                document.uploaded_by = request.user
            document.save()
        for document in formset.deleted_objects:
            document.delete()
        formset.save_m2m()


@admin.register(SchoolDocument)
class SchoolDocumentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "school", "content_type", "size", "uploaded_by", "uploaded_at")
    list_filter = ("content_type",)
    search_fields = ("title", "original_name", "school__name")
    readonly_fields = ("original_name", "content_type", "size", "uploaded_by", "uploaded_at")
    autocomplete_fields = ("school",)

    def save_model(self, request, obj, form, change) -> None:
        if obj.uploaded_by_id is None:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
