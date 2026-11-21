from django.db.models import Count
from django.http import FileResponse
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from apps.accounts.permissions import IsAdminRoleOrReadOnly
from apps.schools.api.serializers import SchoolDocumentSerializer, SchoolSerializer
from apps.schools.models import School, SchoolDocument
from apps.schools.services import document_file_response


class SchoolViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminRoleOrReadOnly]
    search_fields = ("name", "city", "postal_code")
    ordering_fields = ("name", "city", "student_count", "created_at")
    ordering = ("name", "city")

    def get_queryset(self):
        return School.objects.select_related("created_by").annotate(
            document_count=Count("documents")
        )

    def perform_create(self, serializer: SchoolSerializer) -> None:
        serializer.save(created_by=self.request.user)

    @extend_schema(methods=["GET"], responses=SchoolDocumentSerializer(many=True))
    @extend_schema(
        methods=["POST"],
        request={"multipart/form-data": SchoolDocumentSerializer},
        responses={201: SchoolDocumentSerializer},
    )
    @action(
        detail=True,
        methods=["get", "post"],
        serializer_class=SchoolDocumentSerializer,
        parser_classes=[MultiPartParser, FormParser],
    )
    def documents(self, request: Request, pk: str | None = None) -> Response:
        school = self.get_object()
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(school=school, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        queryset = school.documents.select_related("uploaded_by")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter("school", OpenApiTypes.INT, description="Filtrer par identifiant d'école.")
    ]
)
class SchoolDocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SchoolDocumentSerializer
    permission_classes = [IsAdminRoleOrReadOnly]
    parser_classes = [JSONParser]
    search_fields = ("title", "original_name")
    ordering_fields = ("uploaded_at", "size", "title")
    ordering = ("-uploaded_at", "-pk")

    def get_queryset(self):
        queryset = SchoolDocument.objects.select_related("school", "uploaded_by")
        school_id = self.request.query_params.get("school")
        if school_id is None:
            return queryset
        if not school_id.isdigit():
            return queryset.none()
        return queryset.filter(school_id=int(school_id))

    @extend_schema(responses={(200, "application/octet-stream"): OpenApiTypes.BINARY})
    @action(detail=True, methods=["get"])
    def download(self, request: Request, pk: str | None = None) -> FileResponse:
        return document_file_response(self.get_object())
