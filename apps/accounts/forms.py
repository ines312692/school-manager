from django import forms
from django.contrib.auth.forms import AdminUserCreationForm as DjangoAdminUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.accounts.services import email_is_taken


class EmailNormalizationMixin:
    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        instance_pk = self.instance.pk if self.instance else None
        if email_is_taken(email, exclude_pk=instance_pk):
            raise forms.ValidationError(_("Un compte utilise déjà cette adresse e-mail."))
        return email


class SignUpForm(EmailNormalizationMixin, UserCreationForm):
    email = forms.EmailField(label=_("Adresse e-mail"), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")


class AdminUserCreationForm(EmailNormalizationMixin, DjangoAdminUserCreationForm):
    class Meta(DjangoAdminUserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")


class AdminUserChangeForm(EmailNormalizationMixin, DjangoUserChangeForm):
    class Meta(DjangoUserChangeForm.Meta):
        model = User
        fields = "__all__"
