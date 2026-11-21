from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdminRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self) -> bool:
        return self.request.user.is_admin
