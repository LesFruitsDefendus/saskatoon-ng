from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest
from django.utils.translation import gettext_lazy
from member.models import AuthUser


def is_pickleader(user: AuthUser) -> bool:
    return user.groups.filter(name__in=["pickleader"]).exists()


def is_pickleader_or_core(user: AuthUser) -> bool:
    return user.groups.filter(name__in=["pickleader", "core"]).exists()


def is_core_or_admin(user: AuthUser) -> bool:
    return user.groups.filter(name__in=["core", "admin"]).exists()


def is_pickleader_or_core_or_admin(user: AuthUser) -> bool:
    return user.groups.filter(name__in=["pickleader", "core", "admin"]).exists()


def is_translator(user: AuthUser) -> bool:
    return is_core_or_admin(user) and user.is_staff


class IsCoreOrAdmin(IsAuthenticated):
    message = gettext_lazy("Viewing this page is restricted to core and admin users.")

    def has_permission(self, request: HttpRequest, view):
        if super().has_permission(request, view):
            return is_core_or_admin(request.user)
        return False


class IsPickLeaderOrCoreOrAdmin(IsAuthenticated):
    message = gettext_lazy("Viewing this page is restricted to pickleaders, core and admin users.")

    def has_permission(self, request: HttpRequest, view):
        if super().has_permission(request, view):
            return is_pickleader_or_core_or_admin(request.user)
        return False
