from typing import Any, Optional
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _


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
