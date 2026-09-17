from typing import Any, Optional
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class TaggedFormInvalidMixin:
    """Mixin to format form errors with optional extra_tags."""

    request: HttpRequest
    message_extra_tag: Optional[str] = None
    error_field_name: Optional[str] = None

    def get_success_url(self) -> str:
        raise NotImplementedError

    def form_invalid(self, form: Any) -> HttpResponse:
        if self.error_field_name:
            field_errors = form.errors.get(self.error_field_name, [])
        else:
            field_errors = []
            for errors in form.errors.values():
                field_errors.extend(errors)

        if field_errors:
            extra_args = {}
            if self.message_extra_tag:
                extra_args['extra_tags'] = f"component-{self.message_extra_tag}"

            messages.error(self.request, " | ".join(field_errors), **extra_args)

        return HttpResponseRedirect(self.get_success_url())


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
