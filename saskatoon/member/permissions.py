from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy
from django.contrib.auth.models import AnonymousUser
from typing import Union

from member.models import AuthUser, Role

ModelName = str
Action = str
Permissions = dict[ModelName, dict[Action, set[Role]]]

CORE = Role.CORE
PICKLEADER = Role.PICKLEADER

PERMISSIONS: Permissions = {  # pytype: disable=annotation-type-mismatch
    "actor": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "person": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "organization": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "authuser": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "onboarding": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "neighborhood": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "city": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "state": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "country": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
}


def is_pickleader(user: AuthUser) -> bool:
    return user.groups.filter(name__in=[PICKLEADER]).exists()


def is_pickleader_or_core(user: AuthUser) -> bool:
    return user.groups.filter(name__in=[PICKLEADER, CORE]).exists()


def is_core_or_admin(user: Union[AuthUser, AnonymousUser]) -> bool:
    return user.groups.filter(name__in=[CORE, "admin"]).exists()


def is_pickleader_or_core_or_admin(user: AuthUser) -> bool:
    return user.groups.filter(name__in=[PICKLEADER, CORE, "admin"]).exists()


def is_translator(user: AuthUser) -> bool:
    return is_core_or_admin(user) and user.is_staff


class IsCoreOrAdmin(IsAuthenticated):
    message = gettext_lazy("Viewing this page is restricted to core and admin users.")

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            user = request.user
            if not user.is_authenticated:
                return False

            return is_core_or_admin(user)
        return False


class IsPickLeaderOrCoreOrAdmin(IsAuthenticated):
    message = gettext_lazy("Viewing this page is restricted to pickleaders, core and admin users.")

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            user = request.user
            if not user.is_authenticated:
                return False

            return is_pickleader_or_core_or_admin(user)
        return False
