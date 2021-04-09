from dal import autocomplete
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from harvest.filters import HarvestFilter, PropertyFilter, CommunityFilter
from rest_framework import viewsets, permissions
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, CreateView
from django_filters import rest_framework as filters

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

from harvest.forms import EquipmentForm, HarvestYieldForm, CommentForm, RequestForm, PropertyForm, PublicPropertyForm, HarvestForm, PropertyImageForm, RFPManageForm

from member.models import AuthUser, Organization, Actor, Person, City
from .models import Harvest, Property, Equipment, TreeType, RequestForParticipation
from .serializers import ( HarvestSerializer, PropertySerializer, EquipmentSerializer, 
    CommunitySerializer, BeneficiarySerializer, RequestForParticipationSerializer )




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

    # Harvest detail
    def retrieve(self, request, format='html', pk=None):
        self.template_name = 'app/harvest_details.html'
        pk = self.get_object().pk
        response = super(HarvestViewset, self).retrieve(request, pk=pk)
        if format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})

    def list(self, request, *args, **kwargs):
        self.template_name = 'app/harvest_list.html'
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

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, City):
            return str(obj)
        return super().default(obj)

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

    # Property detail
    def retrieve(self, request, format='html', pk=None):
        self.template_name = 'app/property_details.html'
        pk = self.get_object().pk
        response = super(PropertyViewset, self).retrieve(request, pk=pk)

        # This workaround will check if property owner (which is an Actor)
        # is a subclass Person or Organization and will serialize the result.
        # I couldn't find a way to make it happen in the PropertySerializer class.
        #entity = Person.objects.filter(actor_id=response.data['owner'])
        #if not entity:
        #    entity = Organization.objects.filter(actor_id=response.data['owner'])

        #entity_serialized = serialize('json', entity, fields=('city__name'))
        #print(entity_serialized)
        #response.data['owner'] = entity_serialized

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
class EquipmentViewset(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('-id')

    permission_classes = [
      permissions.AllowAny
    ]

    serializer_class = EquipmentSerializer
    template_name = 'app/equipment_list.html'

    def list(self, request, *args, **kwargs):
        # filter_request = self.request.GET

        response = super(EquipmentViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})

# RequestForParticipation Viewset
class RequestForParticipationViewset(viewsets.ModelViewSet):
    queryset = RequestForParticipation.objects.all().order_by('-id')

    permission_classes = [
      permissions.AllowAny
    ]

    serializer_class = RequestForParticipationSerializer
    template_name = 'app/participation_list.html'

    def list(self, request, *args, **kwargs):
        # filter_request = self.request.GET

        response = super(RequestForParticipationViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})

# Beneficiary Viewset
class BeneficiaryViewset(viewsets.ModelViewSet):
    queryset = Organization.objects.all().order_by('-actor_id')

    permission_classes = [
      permissions.AllowAny
    ]

    serializer_class = BeneficiarySerializer
    template_name = 'app/beneficiary_list.html'

    def list(self, request, *args, **kwargs):
        filter_request = self.request.GET

        response = super(BeneficiaryViewset, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'json':
            return response
        # default request format is html:
        return Response({'data': response.data})

# Community Viewset
class CommunityViewset(viewsets.ModelViewSet):
    queryset = AuthUser.objects.filter(person__first_name__isnull=False).order_by('-id')

    ######### Integrating DRF to django-filter #########
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CommunityFilter
    ####################################################

    permission_classes = [
      permissions.AllowAny
    ]

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

############### STANDARD VIEWS #####################

class IndexView(TemplateView):
    template_name = 'app/index.html'

class EquipmentCreateView(SuccessMessageMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'app/equipment_create.html'
    success_url = reverse_lazy('equipment-list')
    success_message = "Equipment created successfully!"

class PropertyCreateView(SuccessMessageMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'app/property_create.html'
    success_url = reverse_lazy('property-list')
    success_message = "Property created successfully!"

class PropertyCreatePublicView(SuccessMessageMixin, CreateView):
    model = Property
    form_class = PublicPropertyForm
    template_name = 'app/property_create_public.html'
    #FIXME: add a public page as response
    success_url = reverse_lazy('property-list')
    success_message = "Property created successfully!"

class HarvestCreateView(SuccessMessageMixin, CreateView):
    model = Harvest
    form_class = HarvestForm
    template_name = 'app/harvest_create.html'
    success_url = reverse_lazy('harvest-list')
    success_message = "Harvest created successfully!"

class RequestForParticipationCreateView(SuccessMessageMixin, CreateView):
    model = RequestForParticipation
    template_name = 'app/participation_create.html'
    form_class = RequestForm
    success_url = reverse_lazy('calendar')
    success_message = "Your request of participation has been sent.\n The pick leader will contact you soon!"

################ AUTOCOMPLETE ###############################

class PickLeaderAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = AuthUser.objects.filter(is_staff=True)

        if self.q:
            qs = qs.filter(person__first_name__istartswith=self.q)

        return qs

class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.q:
            qs = qs.filter(first_name__icontains=self.q)

        return qs

class ActorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Actor.objects.none()

        qs = Actor.objects.all()
        list_actor = []

        if self.q:
            first_name = qs.filter(
                person__first_name__icontains=self.q
            )
            family_name = qs.filter(
                person__family_name__icontains=self.q
            )
            civil_name = qs.filter(
                organization__civil_name__icontains=self.q
            )

            for actor in first_name:
                if actor not in list_actor:
                    list_actor.append(actor)

            for actor in family_name:
                if actor not in list_actor:
                    list_actor.append(actor)

            for actor in civil_name:
                if actor not in list_actor:
                    list_actor.append(actor)

        if not list_actor:
            list_actor = qs

        return list_actor

class TreeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = TreeType.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

class PropertyAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Property.objects.none()

        qs = Property.objects.all()
        list_property = []

        if self.q:
            first_name = qs.filter(
                owner__person__first_name__icontains=self.q
            )
            family_name = qs.filter(
                owner__person__family_name__icontains=self.q
            )

            for actor in first_name:
                if actor not in list_property:
                    list_property.append(actor)

            for actor in family_name:
                if actor not in list_property:
                    list_property.append(actor)
        return qs


class EquipmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Equipment.objects.none()

        qs = Equipment.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
