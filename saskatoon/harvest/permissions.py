from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest
from django.utils.translation import gettext_lazy


class IsCoreOrAdmin(IsAuthenticated):
    message = gettext_lazy("Viewing this page is restricted to core and admin users.")

    def has_permission(self, request: HttpRequest, view):
        if super().has_permission(request, view):
            return request.user.groups.filter(name__in=["core", "admin"]).exists()
        return False
