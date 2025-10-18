from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from harvest.serializers import (
    OrganizationSerializer,
)
from member.models import AuthUser, Organization
from member.filters import (
    CommunityFilter,
    EquipmentPointFilter,
    OrganizationFilter,
)
from member.permissions import (
    IsPickLeaderOrCoreOrAdmin,
    is_core_or_admin
)
from member.serializers import CommunitySerializer
from sitebase.utils import (
    get_filter_context,
    renderer_format_needs_json_response,
)


class OrganizationViewset(LoginRequiredMixin, viewsets.ModelViewSet[Organization]):
    """Organization viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Organization.objects.all().order_by('-actor_id')
    template_name = 'app/detail_views/organization/view.html'
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrganizationFilter
    search_fields = [
        'actor_id',
        'civil_name',
        'contact_person__first_name',
        'contact_person__family_name',
        'contact_person__auth_user__email',
    ]

    def list(self, request, *args, **kwargs):
        """Beneficiairies list view"""

        self.template_name = 'app/list_views/organization/organizations.html'
        response = super().list(request, *args, **kwargs)
        if renderer_format_needs_json_response(request):
            return response

        return Response({
            "data": response.data["results"],
            "count": response.data["count"],
            "next": response.data["next"],
            "previous": response.data["previous"],
            "pages_count": response.data["pages_count"],
            "current_page_number": response.data["current_page_number"],
            "items_per_page": response.data["items_per_page"],
            "filter": get_filter_context(self),
            'new': {
                'url': reverse_lazy('organization-create'),
                'title': _("New Organization"),
            }
        })


class EquipmentPointListView(LoginRequiredMixin, generics.ListAPIView[Organization]):
    """List view for organizations that are equipment points."""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Organization.objects.filter(is_equipment_point=True).order_by('-actor_id')
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = EquipmentPointFilter
    template_name = 'app/list_views/organization/organizations.html'
    search_fields = [
        'actor_id',
        'civil_name',
        'contact_person__first_name',
        'contact_person__family_name',
        'contact_person__auth_user__email',
    ]

    def list(self, request, *args, **kwargs):
        """Equipment Points list view."""

        response = super().list(request, *args, **kwargs)
        if renderer_format_needs_json_response(request):
            return response

        context = {
            'data': response.data["results"],
            'filter': get_filter_context(self, 'equipment-point'),
        }

        # NOTE: Creation of a new Equipment Point is currently only
        # supported in the admin panel due to the Equipment inline form
        # not having yet been implemented. The `New Organization` button
        # is restricted to Core or Admin members and simply links to the
        # Admin creation form. Change the `url` once Equipment Point
        # creation can be done with a conventional view.
        if is_core_or_admin(self.request.user):
            context['new'] = {
                'url': reverse_lazy('admin:member_organization_add'),
                'title': _("New Organization")
            }

        return Response(context)


class CommunityViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Community viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = AuthUser.objects \
                       .filter(person__first_name__isnull=False) \
                       .order_by('-date_joined')
    serializer_class = CommunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CommunityFilter
    search_fields = [
        'id',
        'email',
        'person__first_name',
        'person__family_name'
    ]
    template_name = 'app/list_views/community/view.html'

    def list(self, request, *args, **kwargs):
        response = super(CommunityViewset, self).list(request, *args, **kwargs)
        if renderer_format_needs_json_response(request):
            return response
        return Response(
            {
                "data": response.data["results"],
                "count": response.data["count"],
                "next": response.data["next"],
                "previous": response.data["previous"],
                "pages_count": response.data["pages_count"],
                "current_page_number": response.data["current_page_number"],
                "items_per_page": response.data["items_per_page"],
                "filter": get_filter_context(self),
                "new": {
                    "url": reverse_lazy("person-create"),
                    "title": _("New Person"),
                },
            }
        )
