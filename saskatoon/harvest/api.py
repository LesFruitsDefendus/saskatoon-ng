from rest_framework.response import Response

from .models import Harvest, Property, Equipment
from rest_framework import viewsets, permissions
from .serializers import HarvestSerializer, PropertySerializer, EquipmentSerializer
import django_filters.rest_framework

# Harvest Viewset
class HarvestViewset(viewsets.ModelViewSet):
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filter_fields = ('pick_leader','owner_fruit', 'nb_required_pickers', 'property', 'about')
    queryset = Harvest.objects.all()
    permission_classes = [
      permissions.AllowAny
    ]
    serializer_class = HarvestSerializer
    template_name = 'harvest.html'

    def list(self, request, *args, **kwargs):
        response = super(HarvestViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
             return Response({'data': response.data})
        return response

# Property Viewset
class PropertyViewset(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    permission_classes = [
      permissions.AllowAny
    ]
    serializer_class = PropertySerializer

# Equipment Viewset
class EquipmentViewset(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    template_name = 'equipment.html'
    serializer_class = EquipmentSerializer

    permission_classes = [
      permissions.AllowAny
    ]

    def list(self, request, *args, **kwargs):
        response = super(EquipmentViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
             return Response({'data': response.data})
        return response