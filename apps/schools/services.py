from django.db.models import Count, Q, QuerySet
from django.http import FileResponse, Http404

from apps.schools.models import School, SchoolDocument


def search_schools(term: str | None = None) -> QuerySet[School]:
    queryset = School.objects.annotate(document_count=Count("documents")).order_by("name", "city")
    if term:
        queryset = queryset.filter(
            Q(name__icontains=term) | Q(city__icontains=term) | Q(postal_code__icontains=term)
        )
    return queryset


def school_name_is_taken(name: str, city: str, *, exclude_pk: int | None = None) -> bool:
    queryset = School.objects.filter(name__iexact=name.strip(), city__iexact=city.strip())
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.exists()


def document_file_response(document: SchoolDocument) -> FileResponse:
    try:
        handle = document.file.open("rb")
    except FileNotFoundError as exc:
        raise Http404("Fichier introuvable.") from exc
    return FileResponse(
        handle,
        as_attachment=True,
        filename=document.original_name,
        content_type=document.content_type,
    )
