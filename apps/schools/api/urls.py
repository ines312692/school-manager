from rest_framework.routers import SimpleRouter

from apps.schools.api.views import SchoolDocumentViewSet, SchoolViewSet

app_name = "schools_api"

router = SimpleRouter()
router.register("schools", SchoolViewSet, basename="school")
router.register("documents", SchoolDocumentViewSet, basename="document")

urlpatterns = router.urls
