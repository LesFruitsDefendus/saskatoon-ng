from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class CommentFormInvalidMixin:
    """Mixin to format form errors and redirect on invalid submissions."""

    def form_invalid(self, form):
        content_errors = form.errors.get('content')

        if content_errors:
            messages.error(self.request, " | ".join(content_errors))
        else:
            messages.error(self.request, _("Please correct the error below."))

        return HttpResponseRedirect(self.get_success_url())
