from typing import Any, Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy

from member.models import Organization


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


class EquipmentOrganizationMixin:
    """Return to the Organization page the equipment form was opened from."""

    request: HttpRequest

    def get_organization(self):
        try:
            return Organization.objects.get(actor_id=self.request.GET['aid'])
        except (KeyError, Organization.DoesNotExist):
            return None

    def get_success_url(self):
        org = self.get_organization()
        if org:
            return reverse_lazy('organization-detail', kwargs={'pk': org.actor_id})
        return reverse_lazy('home')
