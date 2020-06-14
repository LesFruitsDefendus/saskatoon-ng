from harvest.models import Harvest, Property
from rest_framework import viewsets, permissions
from .serializers import HarvestSerializer, PropertySerializer
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

# Property Viewset
class PropertyViewset(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    permission_classes = [
      permissions.AllowAny
    ]
    serializer_class = PropertySerializer
