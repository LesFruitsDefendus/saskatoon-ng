from harvest.models import Harvest, Property
from rest_framework import viewsets, permissions
from .serializers import HarvestSerializer, PropertySerializer

# Harvest Viewset
class HarvestViewset(viewsets.ModelViewSet):
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
