from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets
from rest_framework.response import Response

from django_filters import rest_framework as filters
from .filters import ( HarvestFilter, PropertyFilter, EquipmentFilter,
                       OrganizationFilter, CommunityFilter)

from .forms import ( RequestForm, RFPManageForm, CommentForm )

from member.models import AuthUser, Organization
from .models import Equipment, Harvest, Property, RequestForParticipation, Comment

from .serializers import ( HarvestSerializer, PropertySerializer, EquipmentSerializer,
    CommunitySerializer, BeneficiarySerializer, RequestForParticipationSerializer )



# Harvest Viewset
class HarvestViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Harvest.objects.all().order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('pick_leader','owner_fruit', 'nb_required_pickers', 'property', 'about', 'status', 'start_date')
    filterset_class = HarvestFilter
    ####################################################

    serializer_class = HarvestSerializer

    # Harvest detail
    def retrieve(self, request, format='html', pk=None):
        self.template_name = 'app/harvest_details/view.html'
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
        trees = harvest.trees.all()

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
                         'trees': trees,
                         'form_edit_recipient': HarvestYieldForm(),
                        })

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/harvest_list/view.html'
        filter_request = self.request.GET

        # only way I found to generate the filter form
        filter_form = HarvestFilter(
            filter_request,
            self.queryset
        )

        response = super(HarvestViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return Response(response.data)
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})

    def update(request, *args, **kwargs):
        pass

# Property Viewset
class PropertyViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('is_active', 'authorized', 'pending', 'neighborhood', 'trees', 'ladder_available', 'ladder_available_for_outside_picks')
    filterset_class = PropertyFilter
    ####################################################

    serializer_class = PropertySerializer

    # Property detail
    def retrieve(self, request, format='html', pk=None):
        self.template_name = 'app/property_details.html'
        pk = self.get_object().pk
        response = super(PropertyViewset, self).retrieve(request, pk=pk)

        if format == 'json':
            return response
        # default request format is html:
        return Response({'property': response.data})

    # Properties list
    def list(self, request):
        self.template_name = 'app/property_list.html'
        filter_request = self.request.GET

        # only way I found to generate the filter form
        filter_form = PropertyFilter(
            filter_request,
            self.queryset
        )

        response = super(PropertyViewset, self).list(request)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})



# Equipment Viewset
class EquipmentViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EquipmentFilter
    ####################################################

    serializer_class = EquipmentSerializer
    template_name = 'app/equipment_list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET
        filter_form = EquipmentFilter(
            filter_request,
            self.queryset
        )

        response = super(EquipmentViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})

# RequestForParticipation Viewset
class RequestForParticipationViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = RequestForParticipation.objects.all().order_by('-id')

    serializer_class = RequestForParticipationSerializer
    template_name = 'app/participation_list.html'

    def list(self, request, *args, **kwargs):
        response = super(RequestForParticipationViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})

# Beneficiary Viewset
class BeneficiaryViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Organization.objects.all().order_by('-actor_id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = OrganizationFilter
    ####################################################

    serializer_class = BeneficiarySerializer
    template_name = 'app/beneficiary_list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET

        # only way I found to generate the filter form
        filter_form = OrganizationFilter(
            filter_request,
            self.queryset
        )

        response = super(BeneficiaryViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})

# Community Viewset
class CommunityViewset(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = AuthUser.objects.filter(person__first_name__isnull=False).order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CommunityFilter
    ####################################################

    serializer_class = CommunitySerializer
    template_name = 'app/community_list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET

        # only way I found to generate the filter form
        filter_form = CommunityFilter(
            filter_request,
            self.queryset
        )

        response = super(CommunityViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})
