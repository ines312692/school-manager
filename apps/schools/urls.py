from django.urls import path

from apps.schools import views

app_name = "schools"

urlpatterns = [
    path("", views.SchoolListView.as_view(), name="list"),
    path("new/", views.SchoolCreateView.as_view(), name="create"),
    path("<int:pk>/", views.SchoolDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.SchoolUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.SchoolDeleteView.as_view(), name="delete"),
    path(
        "<int:pk>/documents/new/",
        views.SchoolDocumentUploadView.as_view(),
        name="document-upload",
    ),
    path(
        "documents/<int:pk>/download/",
        views.SchoolDocumentDownloadView.as_view(),
        name="document-download",
    ),
    path(
        "documents/<int:pk>/delete/",
        views.SchoolDocumentDeleteView.as_view(),
        name="document-delete",
    ),
]
