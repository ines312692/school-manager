from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import FileResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AdminRoleRequiredMixin
from apps.schools.forms import SchoolDocumentForm, SchoolForm
from apps.schools.models import School, SchoolDocument
from apps.schools.services import document_file_response, search_schools


class SchoolListView(LoginRequiredMixin, ListView):
    template_name = "schools/school_list.html"
    context_object_name = "schools"
    paginate_by = 10

    def get_queryset(self):
        return search_schools(self.request.GET.get("q", "").strip())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class SchoolDetailView(LoginRequiredMixin, DetailView):
    model = School
    template_name = "schools/school_detail.html"
    context_object_name = "school"

    def get_queryset(self):
        return School.objects.select_related("created_by")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.object.documents.select_related("uploaded_by")
        if self.request.user.is_admin:
            context["document_form"] = SchoolDocumentForm()
        return context


class SchoolCreateView(AdminRoleRequiredMixin, SuccessMessageMixin, CreateView):
    model = School
    form_class = SchoolForm
    template_name = "schools/school_form.html"
    success_message = _("L'école « %(name)s » a été créée.")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SchoolUpdateView(AdminRoleRequiredMixin, SuccessMessageMixin, UpdateView):
    model = School
    form_class = SchoolForm
    template_name = "schools/school_form.html"
    success_message = _("L'école « %(name)s » a été mise à jour.")


class SchoolDeleteView(AdminRoleRequiredMixin, DeleteView):
    model = School
    template_name = "schools/school_confirm_delete.html"
    context_object_name = "school"
    success_url = reverse_lazy("schools:list")

    def form_valid(self, form):
        messages.success(self.request, _("L'école « %s » a été supprimée.") % self.object.name)
        return super().form_valid(form)


class SchoolDocumentUploadView(AdminRoleRequiredMixin, CreateView):
    model = SchoolDocument
    form_class = SchoolDocumentForm
    template_name = "schools/document_form.html"

    @cached_property
    def school(self) -> School:
        return get_object_or_404(School, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school"] = self.school
        return context

    def form_valid(self, form):
        form.instance.school = self.school
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, _("Le document « %s » a été ajouté.") % self.object)
        return response

    def get_success_url(self) -> str:
        return self.school.get_absolute_url()


class SchoolDocumentDownloadView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, pk: int) -> FileResponse:
        return document_file_response(get_object_or_404(SchoolDocument, pk=pk))


class SchoolDocumentDeleteView(AdminRoleRequiredMixin, DeleteView):
    model = SchoolDocument
    template_name = "schools/document_confirm_delete.html"
    context_object_name = "document"

    def get_queryset(self):
        return SchoolDocument.objects.select_related("school")

    def get_success_url(self) -> str:
        return reverse("schools:detail", kwargs={"pk": self.object.school_id})

    def form_valid(self, form):
        messages.success(self.request, _("Le document « %s » a été supprimé.") % self.object)
        return super().form_valid(form)
