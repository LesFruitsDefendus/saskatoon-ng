from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, reverse_lazy
from rest_framework import viewsets, generics
from rest_framework.response import Response
from django_filters import rest_framework as filters
from harvest.filters import (EquipmentPointFilter, HarvestFilter, PropertyFilter, EquipmentFilter,
                             OrganizationFilter, CommunityFilter)
from harvest.forms import (RequestForm, RFPManageForm, CommentForm, HarvestYieldForm)
from harvest.models import (HARVESTS_STATUS_CHOICES, Equipment, Harvest, HarvestYield, Property,
                            RequestForParticipation, Comment, TreeType)
from harvest.serializers import (HarvestListSerializer, HarvestSerializer, PropertyListSerializer, PropertySerializer, EquipmentSerializer,
                                 CommunitySerializer, OrganizationSerializer,
                                 RequestForParticipationSerializer)
from harvest.utils import get_similar_properties
from member.models import AuthUser, Organization, Neighborhood, Person
from member.permissions import IsCoreOrAdmin, IsPickLeaderOrCoreOrAdmin, is_core_or_admin


def get_filter_context(viewset, basename=None):
    ''' create filters dictionary for list views
    @param {obj} viewset: rest_framework.viewsets.ModelViewSet subclass instance
    @returns {dic} filters: filters template dictionary
    '''
    f = viewset.filterset_class(viewset.request.GET, viewset.queryset)
    dic = {'form': f.form}
    if any(field in viewset.request.GET for field in set(f.get_fields())):
         dic['reset'] = reverse("{}-list".format(
            basename if basename is not None else viewset.basename
        ))
    return dic


class HarvestViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Harvest viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Harvest.objects.all().order_by('-id')
    serializer_class = HarvestSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HarvestFilter
    filterset_fields = ('pick_leader',
                        'owner_fruit',
                        'nb_required_pickers',
                        'property',
                        'about',
                        'status',
                        'season')

    # Harvest detail
    def retrieve(self, request, format='html', pk=None):
        self.template_name = 'app/detail_views/harvest/view.html'
        pk = self.get_object().pk
        response = super(HarvestViewset, self).retrieve(request, pk=pk)
        if format == 'json':
            return response

        # default request format is html:
        # FIXME: serialize all this

        harvest = Harvest.objects.get(id=self.kwargs['pk'])
        requests = RequestForParticipation.objects.filter(harvest=harvest)
        distribution = HarvestYield.objects.filter(harvest=harvest)
        comments = Comment.objects.filter(harvest=harvest).order_by('-created_date')
        pickers = [r.picker for r in requests.filter(is_accepted=True)]
        if harvest.pick_leader:
          pickers.append(harvest.pick_leader.person)
        organizations = Organization.objects.filter(is_beneficiary=True)
        status_options = (
            harvest_status_choice_tuple[0]
            for harvest_status_choice_tuple
            in HARVESTS_STATUS_CHOICES
            if harvest_status_choice_tuple[0]
            not in (harvest.status, "Adopted", "Orphan")
        )

        return Response({'harvest': response.data,
                         'harvest_date': harvest.get_local_start().strftime("%a. %b. %-d, %Y"),
                         'harvest_start': harvest.get_local_start().strftime("%-I:%M %p"),
                         'harvest_end': harvest.get_local_end().strftime("%-I:%M %p"),
                         'form_request': RequestForm(),
                         'form_comment': CommentForm(),
                         'form_manage_request': RFPManageForm(),
                         'requests': requests,
                         'distribution': distribution,
                         'comments': comments,
                         'property': harvest.property,
                         'pickers': pickers,
                         'organizations': organizations,
                         'form_edit_recipient': HarvestYieldForm(),
                         'status_options': status_options,
                         'about': harvest.about.html,
                        })

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/harvest/view.html'
        self.serializer_class = HarvestListSerializer

        response = super(HarvestViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return Response(response.data)
        # default request format is html:
        return Response({'data': response.data,
                         'filter': get_filter_context(self),
                         'new': {'url': reverse_lazy('harvest-create'),
                                 'title': _("New Harvest")
                                 }
                         })

    def update(request, *args, **kwargs):
        pass


class PropertyViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Property viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Property.objects.all().order_by('-id')
    serializer_class = PropertySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PropertyFilter
    filterset_fields = ('is_active',
                        'authorized',
                        'pending',
                        'neighborhood',
                        'trees',
                        'ladder_available',
                        'ladder_available_for_outside_picks')

    # Property detail
    def retrieve(self, request, format='html', pk=None):
        self.template_name = 'app/detail_views/property/view.html'

        pk = self.get_object().pk
        response = super(PropertyViewset, self).retrieve(request, pk=pk)

        if format == 'json':
            return response

        # default request format is html:
        return Response({'property': response.data,
                         'similar': get_similar_properties(self.get_object())
                         })

    # Properties list
    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/property/view.html'
        self.serializer_class = PropertyListSerializer
        response = super(PropertyViewset, self).list(request)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data,
                         'filter': get_filter_context(self),
                         'new': {'url': reverse_lazy('property-create'),
                                 'title': _("New Property")
                                 }
                         })


class EquipmentViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Equipment viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Equipment.objects.all().order_by('-id')
    serializer_class = EquipmentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EquipmentFilter
    template_name = 'app/list_views/equipment/view.html'

    def list(self, request, *args, **kwargs):
        response = super(EquipmentViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data,
                         'new': {'url': reverse_lazy('equipment-create'),
                                 'title': _("New Equipment"),
                                 },
                         'filter': get_filter_context(self)
                         })


class RequestForParticipationViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Request for participation viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = RequestForParticipation.objects.all().order_by('-id')
    serializer_class = RequestForParticipationSerializer
    template_name = 'app/participation_list.html'

    def list(self, request, *args, **kwargs):
        response = super(RequestForParticipationViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})


class OrganizationViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Organization viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Organization.objects.all().order_by('-actor_id')
    serializer_class = OrganizationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrganizationFilter

    def retrieve(self, request, format='html', pk=None):
        """Organization detail view -  shared by beneficiaries and equipment points."""
        self.template_name = 'app/detail_views/organization/view.html'

        pk = self.get_object().pk
        response = super(OrganizationViewset, self).retrieve(request, pk=pk)

        if format == 'json':
            return response

        # default request format is html:
        return Response({
            'organization': response.data,
            'data': Equipment.objects.filter(owner_id=pk) 
        })

    def list(self, request, *args, **kwargs):
        """Organization list view - accessible via the Beneficiaries menu button."""
        self.template_name = 'app/list_views/organization/view.html'
        response = super(OrganizationViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({
            'data': response.data,
            'filter': get_filter_context(self),
            'new': {
                'url': reverse_lazy('organization-create'),
                'title': _("New Organization"),
            }
        })


class EquipmentPointListView(LoginRequiredMixin, generics.ListAPIView):
    """
    List view for organizations that are equipment points.
    """

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = Organization.objects.filter(is_equipment_point=True).order_by('-actor_id')
    serializer_class = OrganizationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EquipmentPointFilter
    template_name = 'app/list_views/equipment_point/view.html'

    def list(self, request, *args, **kwargs):
        response = super(EquipmentPointListView, self).list(request, *args, **kwargs)

        if request.accepted_renderer.format == 'json':
            return response

        context = {
            'data': response.data,
            'filter': get_filter_context(self, 'equipment-point'),
        }

        # NOTE: Creation of a new Equipment Point is currently only supported in the admin panel
        # due to the Equipment inline form not having yet been implemented.  The `New Organization` 
        # button is restricted to Core or Admin members and simply links to the Admin creation form.
        # Change the `url`  once Equipment Point creation can be done with a conventional form.
        if is_core_or_admin(self.request.user):
            context['new'] = {
                'url': reverse_lazy('admin:member_organization_add'),
                'title': _("New Organization")
            }

        return Response(context)


class CommunityViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Community viewset"""

    permission_classes = [IsPickLeaderOrCoreOrAdmin]
    queryset = AuthUser.objects.filter(person__first_name__isnull=False).order_by('-id')
    serializer_class = CommunitySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CommunityFilter
    template_name = 'app/list_views/community/view.html'

    def list(self, request, *args, **kwargs):
        response = super(CommunityViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data,
                         'filter': get_filter_context(self),
                         'new': {'url': reverse_lazy('person-create'),
                                 'title': _("New Person")
                                 }
                         })


class StatsView(LoginRequiredMixin, generics.ListAPIView):
    """Statistics list view"""

    permission_classes = [IsCoreOrAdmin]
    template_name = "app/stats.html"
    queryset = Harvest.objects.filter(status="Succeeded")
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HarvestFilter
    filterset_fields = ('status', 'season')

    def list(self, request, format="html", *args, **kwargs) -> Response:
        """Returns statistics on harvests for all seasons or a specific season"""
        season = self.request.query_params.get('season')
        self.harvest_queryset = self.filter_queryset(self.get_queryset())
        self.harvest_yield_queryset = HarvestYield.objects.filter(harvest__in=self.harvest_queryset)

        if not self.harvest_queryset:
            messages.error(request, "No harvests were found.", "danger")

        return Response(
            {
                "season": season,
                "seasons": self.filterset_class.YEARS,
                "highlights": self.get_highlights(),
                "total_fruit": self.get_total_weight_harvest_per_fruit(),
                "total_neighborhood": self.get_total_weight_harvest_per_neighborhood(),
                "total_beneficiary": self.get_total_weight_harvest_per_beneficiary(),
                "total_picker": self.get_total_weight_harvest_per_picker(),
            }
        )

    def get_highlights(self) -> dict:
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
