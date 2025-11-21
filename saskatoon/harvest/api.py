from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from rest_framework import generics, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from typing import Dict
from harvest.filters import (
    HarvestFilter,
    PropertyFilter,
    EquipmentFilter,
)
from harvest.models import (
    Equipment,
    Harvest,
    HarvestYield,
    Property,
    RequestForParticipation as RFP,
    TreeType,
)
from harvest.serializers import (
    HarvestListSerializer,
    HarvestDetailSerializer,
    PropertyListSerializer,
    PropertySerializer,
    EquipmentSerializer,
    RequestForParticipationSerializer,
)
from harvest.utils import sum_harvest_yields
from member.models import Organization, Neighborhood, Person
from member.permissions import (
    IsCoreOrAdmin,
    IsPickLeaderOrCoreOrAdmin,
)
from sitebase.utils import (
    get_filter_context,
    renderer_format_needs_json_response,
)


class HarvestViewset(LoginRequiredMixin, viewsets.ModelViewSet[Harvest]):
    """Harvest viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Harvest.objects.all().order_by('-start_date')
    serializer_class = HarvestDetailSerializer
    template_name = 'app/detail_views/harvest/view.html'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = HarvestFilter
    search_fields = [
        'id',
        'property__owner__person__family_name',
        'property__owner__person__first_name',
        'property__street',
        'property__street_number',
    ]

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/harvest/view.html'
        self.serializer_class = HarvestListSerializer
        response = super(HarvestViewset, self).list(request, *args, **kwargs)
        if renderer_format_needs_json_response(request):
            return Response(response.data)

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
                    "url": reverse_lazy("harvest-create"),
                    "title": _("New Harvest"),
                },
            }
        )


class PropertyViewset(LoginRequiredMixin, viewsets.ModelViewSet[Property]):
    """Property viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Property.objects.all().order_by('-id')
    serializer_class = PropertySerializer
    template_name = 'app/detail_views/property/view.html'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PropertyFilter
    search_fields = [
        'id',
        'owner__person__family_name',
        'owner__person__first_name',
        'street',
        'street_number',
        'pending_contact_first_name',
        'pending_contact_family_name',
        'pending_contact_email',
    ]

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/property/view.html'
        self.serializer_class = PropertyListSerializer
        response = super().list(request)
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
                'filter': get_filter_context(self),
                'new': {
                    'url': reverse_lazy('property-create'),
                    'title': _("New Property"),
                },
            }
        )

    def partial_update(self, request, pk=None):
        property = self.get_object()
        response = super().partial_update(request, pk)
        if response.status_code == status.HTTP_200_OK:
            if not property.authorized and request.data.get('authorized'):
                messages.success(request, _("Property successfully authorized!"))
        else:
            messages.error(request, _("Something went wrong"))

        return response


class EquipmentViewset(LoginRequiredMixin, viewsets.ModelViewSet[Equipment]):
    """Equipment viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Equipment.objects.all().order_by('-id')
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = EquipmentFilter
    template_name = 'app/list_views/equipment/view.html'
    search_fields = [
        'type__name_en',
        'type__name_fr',
        'description',
    ]

    def list(self, request, *args, **kwargs):
        response = super(EquipmentViewset, self).list(request, *args, **kwargs)
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
                "new": {
                    "url": reverse_lazy("equipment-create"),
                    "title": _("New Equipment"),
                },
                "filter": get_filter_context(self),
            }
        )


class RFPViewset(LoginRequiredMixin, viewsets.ModelViewSet[RFP]):
    """Request For Participation viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = RFP.objects.all().order_by('-id')
    serializer_class = RequestForParticipationSerializer
    template_name = 'app/participation_list.html'

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
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
            }
        )


class StatsView(LoginRequiredMixin, generics.ListAPIView[Harvest]):
    """Statistics list view"""

    permission_classes = [IsCoreOrAdmin]
    template_name = "app/stats.html"
    queryset = Harvest.objects.filter(status=Harvest.Status.SUCCEEDED)
    filter_backends = [DjangoFilterBackend]
    filterset_class = HarvestFilter
    filterset_fields = ('status', 'season')

    def list(self, request, format="html", *args, **kwargs) -> Response:
        """Returns statistics on harvests for all seasons or a specific season"""

        self.harvest_qs = self.filter_queryset(self.get_queryset())
        self.harvest_yield_qs = HarvestYield.objects.filter(harvest__in=self.harvest_qs)

        if not self.harvest_qs:
            messages.error(request, _("No harvests found for the selected season(s)"))

        return Response(
            {
                "season": self.request.query_params.get('season'),
                "seasons": [choice[0] for choice in Harvest.SEASON_CHOICES],
                "highlights": self.get_highlights(),
                "total_fruit": self.get_total_weight_harvest_per_fruit(request.LANGUAGE_CODE),
                "total_neighborhood": self.get_total_weight_harvest_per_neighborhood(),
                "total_beneficiary": self.get_total_weight_harvest_per_beneficiary(),
                "total_picker": self.get_total_weight_harvest_per_picker(),
            }
        )

    def get_highlights(self) -> Dict[str, int]:
        """Returns general statistics of harvests"""
        total_weight = 0
        if self.harvest_qs:
            total_weight = sum_harvest_yields(self.harvest_yield_qs) or 0

        return {
            "total_beneficiaries": self.get_total_number_beneficiaries(),
            "total_pickers": self.harvest_yield_qs.values("recipient").distinct().count(),
            "total_weight": total_weight,
            "total_harvests": self.harvest_qs.count(),
        }

    def get_total_number_beneficiaries(self) -> int:
        """Returns total number of beneficiary organizations"""
        if not self.harvest_qs:
            return 0

        total_number_beneficiaries = 0
        for org in Organization.objects.all():
            if self.harvest_yield_qs.filter(recipient=org).exists():
                total_number_beneficiaries += 1

        return total_number_beneficiaries

    def get_total_weight_harvest_per_fruit(self, lang='fr'):
        """Returns total number of harvests and weight per fruit"""
        if not self.harvest_qs:
            return []

        total_weight_harvests_per_fruit = []

        for tree in TreeType.objects.all():
            total_weight = sum_harvest_yields(self.harvest_yield_qs.filter(tree=tree))

            if total_weight is not None:
                total_harvests = self.harvest_qs.filter(trees__in=[tree]).count()
                total_weight_harvests_per_fruit.append(
                    (tree.get_fruit_name(lang), total_harvests, total_weight)
                )

        return total_weight_harvests_per_fruit

    def get_total_weight_harvest_per_neighborhood(self):
        """Returns total number of harvests and weight per neighborhood"""
        if not self.harvest_qs:
            return []

        total_weight_harvests_per_neighborhood = []
        for neighborhood in Neighborhood.objects.all().order_by("name"):
            total_weight = sum_harvest_yields(
                self.harvest_yield_qs.filter(harvest__property__neighborhood=neighborhood)
            )
            if total_weight is not None:
                total_harvests = self.harvest_qs.filter(
                    property__neighborhood=neighborhood
                ).count()
                total_weight_harvests_per_neighborhood.append(
                    (neighborhood, total_harvests, total_weight)
                )

        return total_weight_harvests_per_neighborhood

    def get_total_weight_harvest_per_beneficiary(self):
        """Returns total number of harvests and weight per beneficiary organization"""
        if not self.harvest_qs:
            return []

        total_weight_harvests_per_beneficiary = []

        for beneficiary in Organization.objects.filter(is_beneficiary=True):
            total_weight = sum_harvest_yields(self.harvest_yield_qs.filter(recipient=beneficiary))
            if total_weight is not None:
                total_harvests = self.harvest_yield_qs.filter(recipient=beneficiary).count()
                total_weight_harvests_per_beneficiary.append(
                    (beneficiary, total_harvests, total_weight)
                )

        return total_weight_harvests_per_beneficiary

    def get_total_weight_harvest_per_picker(self):
        """Returns total number of harvests and weight per picker"""
        if not self.harvest_qs:
            return []

        pickers = Person.objects.all().order_by("first_name")
        total_weight_harvests_per_picker = []

        for p in pickers:
            total_weight = sum_harvest_yields(self.harvest_yield_qs.filter(recipient=p))
            total_harvests_leader = self.harvest_qs.filter(pick_leader__person=p).count()
            total_harvests_rfp = RFP.objects.filter(person=p).count()
            total_harvests_accepted = RFP.objects.filter(
                person=p, status=RFP.Status.ACCEPTED
            ).count()
            total_harvests_recipient = self.harvest_yield_qs.filter(recipient=p).count()

            if total_weight is not None:
                total_weight_harvests_per_picker.append(
                    (
                        p,
                        total_harvests_leader,
                        total_harvests_rfp,
                        total_harvests_accepted,
                        total_harvests_recipient,
                        total_weight,
                    )
                )

        return total_weight_harvests_per_picker
