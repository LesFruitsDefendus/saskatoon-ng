from dal import autocomplete
from .models import TreeType, Property, Equipment
from django.db.models.query_utils import Q


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

        if self.q:
            q0 = Q(street_number__icontains=self.q)
            q1 = Q(street__icontains=self.q)
            q2 = Q(owner__person__first_name__icontains=self.q)
            q3 = Q(owner__person__family_name__icontains=self.q)
            qs = qs.filter(q0 | q1 | q2 | q3)

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
