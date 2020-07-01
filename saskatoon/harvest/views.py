from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import mixins
from rest_framework import viewsets

class EquipmentList(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    template_name = 'equipment.html'

    def get(self, request, *args, **kwargs):
        data = EquipmentSerializer([]).data
        if request.accepted_renderer.format == 'html':
             return Response(data, template_name='equipment.html')
        return Response(data)
    #
    # def post(self, request, *args, **kwargs):
    #     return self.create(request, *args, **kwargs)