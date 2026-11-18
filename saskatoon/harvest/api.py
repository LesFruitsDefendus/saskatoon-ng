from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from harvest.filters import (
    EquipmentFilter,
    HarvestFilter,
    PropertyFilter,
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
    EquipmentSerializer,
    HarvestDetailSerializer,
    HarvestListSerializer,
    HarvestMapSerializer,
    HarvestSerializer,
    PropertyListSerializer,
    PropertyMapSerializer,
    PropertySerializer,
    RequestForParticipationSerializer,
    StatsSerializer,
)
from member.models import Organization, Person
from member.permissions import (
    IsCoreOrAdmin,
    IsPickLeaderOrCoreOrAdmin,
)
from member.utils import get_available_equipment_points
from sitebase.models import Email, EmailType
from sitebase.serializers import EmailPropertySerializer
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

    def get_serializer_class(self):
        if self.action == 'list':
            return HarvestListSerializer
        if self.action == 'map':
            return HarvestMapSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/harvest/view.html'
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

    def map_marker_info(self, request, pk=None):
        """Harvest details displayed in map pop-up window"""

        self.template_name = 'app/list_views/harvest/marker.html'
        harvest = self.get_object()

        serialized = HarvestSerializer(harvest)
        return Response(serialized.data)

    def map(self, request, *args, **kwargs):
        """Harvest map view."""

        self.template_name = 'app/list_views/harvest/map.html'
        self.pagination_class = None
        response = super().list(request, *args, **kwargs)

        if renderer_format_needs_json_response(request):
            return response

        return Response(
            {
                "data": response.data,
                'filter': get_filter_context(self, 'harvest'),
                'new': {
                    'url': reverse_lazy('harvest-create'),
                    'title': _("New Harvest"),
                },
            }
        )

    @action(methods=['post'], detail=True, permission_classes=[IsPickLeaderOrCoreOrAdmin])
    def cancel_reservation(self, request, pk=None):
        harvest = self.get_object()
        harvest.equipment_reserved.set([])

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @action(methods=['post'], detail=True, permission_classes=[IsPickLeaderOrCoreOrAdmin])
    def make_reservation(self, request, pk=None):
        try:
            org: int = int(request.data.get('org'))
        except (TypeError, ValueError):
            messages.error(request, _("Missing Organization id"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except Organization.DoesNotExist:
            messages.error(request, _("Organization does not exist"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            harvest = Harvest.objects.get(pk=pk)
        except Harvest.DoesNotExist:
            messages.error(request, _("Harvest does not exist"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if harvest.start_date is None or harvest.end_date is None:
            messages.error(request, _("Harvest dates must be set before reserving equipment"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            available = get_available_equipment_points(
                harvest.start_date, harvest.end_date, harvest
            ).get(actor_id=org)

            harvest.equipment_reserved.set(Equipment.objects.filter(owner=available))
            harvest.save()
            messages.success(request, _("Your reservation was successful!"))
        except Organization.DoesNotExist:
            messages.error(request, _("Sorry, this equipment point is no longer available"))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        if self.action == 'map':
            return PropertyMapSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/property/view.html'
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

    def map_marker_info(self, request, pk=None):
        """Property details displayed in map pop-up window"""

        self.template_name = 'app/list_views/property/marker.html'
        property = self.get_object()

        serialized = PropertySerializer(property)
        return Response(serialized.data)

    def partial_update(self, request, pk=None):
        property = self.get_object()
        response = super().partial_update(request, pk)
        if response.status_code == status.HTTP_200_OK:
            if not property.authorized and request.data.get('authorized'):
                messages.success(request, _("Property successfully authorized!"))
        else:
            messages.error(request, _("Something went wrong"))

        return response

    @action(methods=['post'], detail=True, permission_classes=[IsCoreOrAdmin])
    def send_authorization_email(self, request, pk=None):
        property = self.get_object()
        recipient = property.email_recipient
        if recipient is None:
            messages.error(request, _("No email address associated with property!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if Email.objects.create(
            recipient=recipient,
            type=EmailType.SEASON_AUTHORIZATION,
        ).send(data=dict(EmailPropertySerializer(property).data)):
            messages.success(
                request,
                _("Authorization email successfully sent to {email}!").format(
                    email=recipient.email
                ),
            )
        else:
            messages.error(
                request,
                _("Could not send authorization email to {email}.").format(email=recipient.email),
            )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def map(self, request, *args, **kwargs):
        """Property map view."""

        self.template_name = 'app/list_views/property/map.html'
        self.pagination_class = None
        response = super().list(request, *args, **kwargs)

        if renderer_format_needs_json_response(request):
            return response

        return Response(
            {
                "data": response.data,
                'filter': get_filter_context(self, 'property'),
                'new': {
                    'url': reverse_lazy('property-create'),
                    'title': _("New Property"),
                },
            }
        )


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


WEIGHT = Sum("total_in_lb")


class StatsView(LoginRequiredMixin, generics.GenericAPIView[Harvest]):
    permission_classes = [IsCoreOrAdmin]
    template_name = "app/stats.html"
    queryset = Harvest.objects.filter(status=Harvest.Status.SUCCEEDED)
    filterset_class = HarvestFilter

    def get(self, request, *args, **kwargs):
        harvests = self.filter_queryset(self.get_queryset())
        yields = HarvestYield.objects.filter(harvest__in=harvests)

        if not harvests.exists():
            messages.error(request, _("No harvests found for the selected season(s)"))

        pickers = self.per_picker(harvests, yields)
        beneficiaries = self.per_beneficiary(yields)
        stats = {
            "season": request.query_params.get("season"),
            "highlights": {
                "total_harvests": harvests.count(),
                "total_weight": yields.aggregate(w=WEIGHT)["w"] or 0,
                "total_pickers": yields.values("recipient").distinct().count(),
                "total_beneficiaries": Organization.objects.filter(
                    pk__in=yields.values("recipient")
                ).count(),
            },
            "fruits": self.per_fruit(harvests, yields, request.LANGUAGE_CODE),
            "neighborhoods": self.per_neighborhood(harvests, yields),
            "beneficiaries": beneficiaries,
            "pickers": pickers,
        }
        data = StatsSerializer(stats).data
        data["seasons"] = [c[0] for c in Harvest.SEASON_CHOICES]
        return Response(data)

    def per_fruit(self, harvests, yields, lang="fr"):
        weights = {
            r["tree"]: r["weight"]
            for r in yields.values("tree").annotate(weight=WEIGHT).order_by()
        }
        # harvests whose trees include the fruit, yielded or not
        counts = dict(harvests.values_list("trees").annotate(n=Count("id")).order_by())
        return [
            {
                "fruit_name": tree.get_fruit_name(lang),
                "harvests": counts.get(tree.pk, 0),
                "weight": weights[tree.pk],
            }
            for tree in TreeType.objects.filter(pk__in=list(weights))
        ]

    def per_neighborhood(self, harvests, yields):
        rows = (
            yields.filter(harvest__property__neighborhood__isnull=False)
            .values(borough=F("harvest__property__neighborhood__name"))
            .annotate(weight=WEIGHT)
            .order_by("borough")
        )
        # every succeeded harvest in the neighborhood, with or without yields
        counts = dict(
            harvests.values_list("property__neighborhood__name").annotate(n=Count("id")).order_by()
        )
        return [{**r, "harvests": counts.get(r["borough"], 0)} for r in rows]

    def per_beneficiary(self, yields):
        rows = {
            r["recipient"]: r
            for r in yields.filter(recipient__organization__is_beneficiary=True)
            .values("recipient")
            # BUG: counts yield rows, not harvests
            .annotate(weight=WEIGHT, harvests=Count("id"))
            .order_by()
        }
        return [
            {
                "beneficiary": org,
                "harvests": rows[org.pk]["harvests"],
                "weight": rows[org.pk]["weight"],
            }
            for org in Organization.objects.filter(pk__in=list(rows))
        ]

    def per_picker(self, harvests, yields):
        received = {
            r["recipient"]: r
            for r in yields.filter(recipient__person__isnull=False)
            .values("recipient")
            .annotate(weight=WEIGHT, as_recipient=Count("id"))
            .order_by()
        }
        ids = list(received)
        led = dict(
            harvests.filter(pick_leader__person__in=ids)
            .values_list("pick_leader__person")
            .annotate(n=Count("id"))
            .order_by()
        )
        rfps = {
            r["person"]: r
            for r in RFP.objects.filter(person__in=ids)
            .values("person")
            .annotate(
                requests=Count("id"),
                accepted=Count("id", filter=Q(status=RFP.Status.ACCEPTED)),
            )
            .order_by()
        }
        return [
            {
                "picker": p,
                "as_leader": led.get(p.pk, 0),
                "requests": rfps.get(p.pk, {}).get("requests", 0),
                "accepted": rfps.get(p.pk, {}).get("accepted", 0),
                "as_recipient": received[p.pk]["as_recipient"],
                "weight": received[p.pk]["weight"],
            }
            for p in Person.objects.filter(pk__in=ids).order_by("first_name")
        ]
