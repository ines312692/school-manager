from rest_framework.permissions import SAFE_METHODS, BasePermission


def _is_authenticated(request) -> bool:
    return bool(request.user and request.user.is_authenticated)


class IsAdminRole(BasePermission):
    message = "Cette action est réservée aux administrateurs."

    def has_permission(self, request, view) -> bool:
        return _is_authenticated(request) and request.user.is_admin


class IsAdminRoleOrReadOnly(BasePermission):
    message = "Cette action est réservée aux administrateurs."

    def has_permission(self, request, view) -> bool:
        if not _is_authenticated(request):
            return False
        return request.method in SAFE_METHODS or request.user.is_admin
