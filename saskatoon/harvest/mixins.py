from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class TaggedFormInvalidMixin:
    """Mixin to format form errors with optional extra_tags."""

    message_extra_tag = None
    error_field_name = None

    def form_invalid(self, form):
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

    success_message = None
    message_extra_tag = None

    def form_valid(self, form):
        response = super().form_valid(form)

        extra_args = {}
        if self.message_extra_tag:
            extra_args['extra_tags'] = f"component-{self.message_extra_tag}"

        messages.success(self.request, self.success_message, **extra_args)
        return response
