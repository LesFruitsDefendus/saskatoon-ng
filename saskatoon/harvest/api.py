from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse, reverse_lazy
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters import rest_framework as filters
from harvest.filters import (HarvestFilter, PropertyFilter, EquipmentFilter,
                             OrganizationFilter, CommunityFilter)
from harvest.forms import (RequestForm, RFPManageForm, CommentForm, HarvestYieldForm)
from member.models import AuthUser, Organization
from harvest.models import (Equipment, Harvest, HarvestYield, Property,
                            RequestForParticipation, Comment)
from harvest.serializers import (HarvestSerializer, PropertySerializer, EquipmentSerializer,
                                 CommunitySerializer, BeneficiarySerializer,
                                 RequestForParticipationSerializer)
from harvest.utils import get_similar_properties


def get_filter_context(viewset):
    ''' create filters dictionary for list views
    @param {obj} viewset: rest_framework.viewsets.ModelViewSet subclass instance
    @returns {dic} filters: filters template dictionary
    '''
    f = viewset.filterset_class(viewset.request.GET, viewset.queryset)
    dic = {'form': f.form}
    if any(field in viewset.request.GET for field in set(f.get_fields())):
        dic['reset'] = reverse(viewset.basename + '-list')
    return dic


class HarvestViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Harvest viewset"""

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
        property = harvest.property
        pickers = [harvest.pick_leader] + [r.picker for r in requests.filter(is_accepted=True)]
        organizations = Organization.objects.filter(is_beneficiary=True)

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
                         'property': property,
                         'pickers': pickers,
                         'organizations': organizations,
                         'form_edit_recipient': HarvestYieldForm(),
                         #! DELETE THIS
                         'statuses': ['status 1', 'status 2']
                        })

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/list_views/harvest/view.html'

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

    queryset = RequestForParticipation.objects.all().order_by('-id')
    serializer_class = RequestForParticipationSerializer
    template_name = 'app/participation_list.html'

    def list(self, request, *args, **kwargs):
        response = super(RequestForParticipationViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})


class BeneficiaryViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Beneficiary viewset"""

    queryset = Organization.objects.all().order_by('-actor_id')
    serializer_class = BeneficiarySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrganizationFilter
    template_name = 'app/list_views/beneficiary/view.html'

    def list(self, request, *args, **kwargs):
        response = super(BeneficiaryViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data,
                         'filter': get_filter_context(self),
                         'new': {'url': reverse_lazy('beneficiary-create'),
                                 'title': _("New Organization")
                                 }
                         })


class CommunityViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    """Community viewset"""

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
