from harvest.models import Harvest
from rest_framework import viewsets, permissions
from .serializers import HarvestSerializer

# Harvest Viewset
class HarvestViewset(viewsets.ModelViewSet):
    queryset = Harvest.objects.all()
    permission_classes = [
      permissions.AllowAny
    ]
    serializer_class = HarvestSerializer
