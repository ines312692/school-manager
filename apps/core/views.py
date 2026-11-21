from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.database import is_database_available

HealthCheckResponseSerializer = inline_serializer(
    name="HealthCheckResponse",
    fields={"status": serializers.CharField(), "database": serializers.CharField()},
)


class HealthCheckView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: HealthCheckResponseSerializer, 503: HealthCheckResponseSerializer}
    )
    def get(self, request: Request) -> Response:
        if is_database_available():
            return Response({"status": "ok", "database": "ok"})
        return Response(
            {"status": "degraded", "database": "unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
