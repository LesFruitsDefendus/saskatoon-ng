from dal import autocomplete
from django.contrib.auth.models import Group
from django.db.models.query_utils import Q
from django import forms
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from member.models import (
    AuthUser,
    Organization,
    Person,
    Neighborhood
)


class CommunityFilter(filters.FilterSet):
    "Community filter"

    class Meta:
        model = AuthUser
        fields = [
            'role',
            'neighborhood',
            'language',
        ]

    role = filters.MultipleChoiceFilter(
        choices=AuthUser.GROUPS,
        label=_("Role(s)"),
        widget=forms.CheckboxSelectMultiple,
        method='role_filter'
    )

    neighborhood = filters.ModelChoiceFilter(
        field_name='person__neighborhood',
        queryset=Neighborhood.objects.all(),
        label=_("Neighborhood"),
    )

    language = filters.ChoiceFilter(
        field_name='person__language',
        choices=Person.Language.choices,
        label=_("Language"),
    )

    def role_filter(self, queryset, name, roles):
        groups = Group.objects.filter(name__in=roles)
        return queryset.filter(groups__in=groups)

    def person_first_name_filter(self, queryset, name, value):
        query = (Q(person__first_name__icontains=value))
        return queryset.filter(query)

    def person_family_name_filter(self, queryset, name, value):
        query = (Q(person__family_name__icontains=value))
        return queryset.filter(query)


class OrganizationFilter(filters.FilterSet):
    """Organization filter"""

    class Meta:
        model = Organization
        fields = [
            'type',
            'neighborhood',
        ]

    type = filters.ChoiceFilter(
        label=_("Type"),
        choices=[
            ('1', _('Beneficiaries')),
            ('2', _('Equipment Points')),
        ],
        method='type_filter'
    )

    neighborhood = filters.ModelChoiceFilter(
        label=_("Neighborhood"),
        queryset=Neighborhood.objects.all(),
        widget=autocomplete.ModelSelect2('neighborhood-autocomplete'),
    )

    def type_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(is_beneficiary=True)
        if value == '2':
            return queryset.filter(is_equipment_point=True)
        return queryset


class EquipmentPointFilter(filters.FilterSet):
    """Equipment Point filter"""

    class Meta:
        model = Organization
        fields = [
            'beneficiary',
            'equipment__type',
            'neighborhood',
        ]

    beneficiary = filters.BooleanFilter(
        field_name='is_beneficiary',
        label=_("Beneficiary"),
        widget=forms.CheckboxInput,
        method='beneficiary_filter'
    )

    neighborhood = filters.ModelChoiceFilter(
        label=_("Neighborhood"),
        queryset=Neighborhood.objects.all(),
        widget=autocomplete.ModelSelect2('neighborhood-autocomplete'),
    )

    def beneficiary_filter(self, queryset, name, value):
        if value:
            return queryset.filter(is_beneficiary=True)
        return queryset
