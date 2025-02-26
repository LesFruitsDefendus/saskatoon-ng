from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from typing import Dict
from harvest.filters import (
    HarvestFilter,
    PropertyFilter,
    EquipmentFilter,
    SEASON_FILTER_CHOICES
)
from harvest.models import (
    Equipment,
    Harvest,
    HarvestYield,
    Property,
    RequestForParticipation,
    TreeType
)
from harvest.serializers import (
    HarvestListSerializer,
    HarvestDetailSerializer,
    PropertyListSerializer,
    PropertySerializer,
    EquipmentSerializer,
    RequestForParticipationSerializer,
)
from member.models import Organization, Neighborhood, Person
from member.permissions import (
    IsCoreOrAdmin,
    IsPickLeaderOrCoreOrAdmin,
)
from sitebase.utils import (
    get_filter_context,
    renderer_format_needs_json_response,
)


class HarvestViewset(LoginRequiredMixin, viewsets.ModelViewSet):
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


class PropertyViewset(LoginRequiredMixin, viewsets.ModelViewSet):
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
    ]

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/property/view.html'
        self.serializer_class = PropertyListSerializer
        response = super(PropertyViewset, self).list(request)
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
                    'title': _("New Property")
                    }
            }
        )


class EquipmentViewset(LoginRequiredMixin, viewsets.ModelViewSet):
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


class RFPViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Request For Participation viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = RequestForParticipation.objects.all().order_by('-id')
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


class StatsView(LoginRequiredMixin, generics.ListAPIView):
    """Statistics list view"""

    permission_classes = [IsCoreOrAdmin]
    template_name = "app/stats.html"
    queryset = Harvest.objects.filter(status=Harvest.Status.SUCCEEDED)
    filter_backends = [DjangoFilterBackend]
    filterset_class = HarvestFilter
    filterset_fields = ('status', 'season')

    def list(self, request, format="html", *args, **kwargs) -> Response:
        """Returns statistics on harvests for all seasons or a specific season"""
        self.harvest_queryset = self.filter_queryset(self.get_queryset())
        self.harvest_yield_queryset = \
            HarvestYield.objects.filter(harvest__in=self.harvest_queryset)

        if not self.harvest_queryset:
            messages.error(
                request,
                _("No harvests found for the selected season(s)"),
                "danger",
            )

        return Response(
            {
                "season": self.request.query_params.get('season'),
                "seasons": [choice[0] for choice in SEASON_FILTER_CHOICES],
                "highlights": self.get_highlights(),
                "total_fruit": self.get_total_weight_harvest_per_fruit(),
                "total_neighborhood": self.get_total_weight_harvest_per_neighborhood(),
                "total_beneficiary": self.get_total_weight_harvest_per_beneficiary(),
                "total_picker": self.get_total_weight_harvest_per_picker(),
            }
        )

    def get_highlights(self) -> Dict[str, int]:
        """Returns general statistics of harvests"""
        total_beneficiaries = self.get_total_number_beneficiaries()
        total_pickers = (
            self.harvest_yield_queryset.values("recipient").distinct().count()
        )
        if not self.harvest_queryset:
            total_weight, total_harvests = 0, 0
        else:
            total_weight = int(
                self.harvest_yield_queryset.aggregate(Sum("total_in_lb")).get(
                    "total_in_lb__sum"
                )
            )
            total_harvests = self.harvest_queryset.count()

        return {
            "total_beneficiaries": total_beneficiaries,
            "total_pickers": total_pickers,
            "total_weight": total_weight,
            "total_harvests": total_harvests,
        }

    def get_total_number_beneficiaries(self) -> int:
        """Returns total number of beneficiary organizations"""
        if not self.harvest_queryset:
            return 0

        beneficiaries = Organization.objects.all()
        total_number_beneficiaries = []

        for beneficiary in beneficiaries:
            total = self.harvest_yield_queryset.filter(recipient=beneficiary).aggregate(
                Sum("total_in_lb")
            )
            # ? If beneficiary got some fruit
            if total.get("total_in_lb__sum") is not None:
                total_number_beneficiaries.append(beneficiary)

        return len(total_number_beneficiaries)

    def get_total_weight_harvest_per_fruit(self):
        """Returns total number of harvests and weight per fruit"""
        if not self.harvest_queryset:
            return []

        treetypes = TreeType.objects.all().order_by("fruit_name")
        total_weight_harvests_per_fruit = []

        for treetype in treetypes:
            total_weight = self.harvest_yield_queryset.filter(tree=treetype).aggregate(
                Sum("total_in_lb")
            )
            total_harvests = self.harvest_queryset.filter(trees__in=[treetype]).count()

            if total_weight.get("total_in_lb__sum") is not None:
                total_weight_harvests_per_fruit.append(
                    (
                        treetype.fruit_name,
                        total_harvests,
                        total_weight.get("total_in_lb__sum"),
                    )
                )

        return total_weight_harvests_per_fruit

    def get_total_weight_harvest_per_neighborhood(self):
        """Returns total number of harvests and weight per neighborhood"""
        if not self.harvest_queryset:
            return []

        neighborhoods = Neighborhood.objects.all().order_by("name")
        total_weight_harvests_per_neighborhood = []

        for neighborhood in neighborhoods:
            total_weight = self.harvest_yield_queryset.filter(
                harvest__property__neighborhood=neighborhood
            ).aggregate(Sum("total_in_lb"))
            total_harvests = self.harvest_queryset.filter(
                property__neighborhood=neighborhood
            ).count()

            if total_weight.get("total_in_lb__sum") is not None:
                total_weight_harvests_per_neighborhood.append(
                    (neighborhood, total_harvests, total_weight.get("total_in_lb__sum"))
                )

        return total_weight_harvests_per_neighborhood

    def get_total_weight_harvest_per_beneficiary(self):
        """Returns total number of harvests and weight per beneficiary organization"""
        if not self.harvest_queryset:
            return []

        beneficiaries = Organization.objects.filter(is_beneficiary=True).order_by(
            "civil_name"
        )
        total_weight_harvests_per_beneficiary = []

        for beneficiary in beneficiaries:
            total_weight = self.harvest_yield_queryset.filter(
                recipient=beneficiary
            ).aggregate(Sum("total_in_lb"))
            total_harvests = self.harvest_yield_queryset.filter(
                recipient=beneficiary
            ).count()

            if total_weight.get("total_in_lb__sum") is not None:
                total_weight_harvests_per_beneficiary.append(
                    (beneficiary, total_harvests, total_weight.get("total_in_lb__sum"))
                )

        return total_weight_harvests_per_beneficiary

    def get_total_weight_harvest_per_picker(self):
        """Returns total number of harvests and weight per picker"""
        if not self.harvest_queryset:
            return []

        pickers = Person.objects.all().order_by("first_name")
        total_weight_harvests_per_picker = []

        for picker in pickers:
            total_weight = self.harvest_yield_queryset.filter(
                recipient=picker
            ).aggregate(Sum("total_in_lb"))
            total_harvests_leader = self.harvest_queryset.filter(
                pick_leader__person=picker
            ).count()
            total_harvests_rfp = RequestForParticipation.objects.filter(
                picker=picker
            ).count()
            total_harvests_is_accepted = (
                RequestForParticipation.objects.filter(picker=picker)
                .filter(is_accepted=True)
                .count()
            )
            total_harvests_recipient = self.harvest_yield_queryset.filter(
                recipient=picker
            ).count()

            if total_weight.get("total_in_lb__sum") is not None:
                total_weight_harvests_per_picker.append(
                    (
                        picker,
                        total_harvests_leader,
                        total_harvests_rfp,
                        total_harvests_is_accepted,
                        total_harvests_recipient,
                        total_weight.get("total_in_lb__sum"),
                    )
                )

        return total_weight_harvests_per_picker
