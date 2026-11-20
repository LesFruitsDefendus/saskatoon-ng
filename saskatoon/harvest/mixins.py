from typing import Any, Callable, Optional

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpRequest, HttpResponse

from member.permissions import is_core_or_admin


class TaggedSuccessMessageMixin:
    """Mixin to handle custom success messages with optional extra_tags."""

    request: HttpRequest
    success_message: Any = None
    message_extra_tag: Optional[str] = None

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)  # type: ignore[misc]

        extra_args = {}
        if self.message_extra_tag:
            extra_args['extra_tags'] = f"component-{self.message_extra_tag}"

        messages.success(self.request, self.success_message, **extra_args)
        return response


class UploaderOrAdminRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Only the uploader and core/admin users may access."""

    request: HttpRequest
    get_object: Callable[..., Any]

    def has_permission(self):
        user = self.request.user
        return self.get_object().uploaded_by == user or is_core_or_admin(user)
