from rest_framework.response import Response
from harvest.forms import HarvestYieldForm, CommentForm, RequestForm, PropertyForm, PublicPropertyForm, \
    HarvestForm, PropertyImageForm, EquipmentForm, RFPManageForm, HarvestYieldForm
from .models import Harvest, Property, Equipment
from harvest.filters import HarvestFilter, PropertyFilter
from rest_framework import viewsets, permissions
from .serializers import HarvestSerializer, PropertySerializer, EquipmentSerializer
import django_filters.rest_framework
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django_filters import rest_framework as filters


#@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'app/index.html'

# Harvest Viewset
class HarvestViewset(viewsets.ModelViewSet):
    queryset = Harvest.objects.all().order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('pick_leader','owner_fruit', 'nb_required_pickers', 'property', 'about', 'status', 'start_date')
    filterset_class = HarvestFilter
    ####################################################

    permission_classes = [
      permissions.AllowAny
    ]

    serializer_class = HarvestSerializer
    template_name = 'harvest/list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET

        # only way I found to generate the filter form
        filter_form = HarvestFilter(
            filter_request,
            self.queryset
        )

        response = super(HarvestViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})

# Property Viewset
class PropertyViewset(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('s_active','authorized', 'pending', 'neighborhood', 'trees', 'ladder_available', 'ladder_available_for_outside_picks')
    filterset_class = PropertyFilter
    ####################################################

    permission_classes = [
      permissions.AllowAny
    ]

    serializer_class = PropertySerializer
    template_name = 'properties/list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET

        # only way I found to generate the filter form
        filter_form = PropertyFilter(
            filter_request,
            self.queryset
        )

        response = super(PropertyViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data, 'form': filter_form.form})

# Equipment Viewset
class EquipmentViewset(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('-id')

    permission_classes = [
      permissions.AllowAny
    ]

    serializer_class = EquipmentSerializer
    template_name = 'equipment/list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET

        response = super(EquipmentViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})

# Equipment Viewset
class OrganizationViewset(viewsets.ModelViewSet):
    pass
