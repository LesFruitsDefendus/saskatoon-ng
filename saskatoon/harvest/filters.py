from datetime import datetime
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Group
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from harvest.models import (Harvest, HARVESTS_STATUS_CHOICES, TreeType,
                            Property, Equipment,  EquipmentType)
from member.models import Language, AuthUser, Neighborhood, Organization


SEASON_FILTER_RANGE = (2016, datetime.now().year)


class HarvestFilter(filters.FilterSet):

    YEARS = list(range(SEASON_FILTER_RANGE[0], SEASON_FILTER_RANGE[1]+1))

    season = filters.ChoiceFilter(
        field_name='start_date',
        choices=[(year, year) for year in YEARS],
        label=_("Season"),
        lookup_expr='year',
        help_text="",
    )

    status = filters.ChoiceFilter(
        choices=list(HARVESTS_STATUS_CHOICES),
        help_text="",
    )

    pick_leader = filters.ModelChoiceFilter(
        queryset=AuthUser.objects.filter(
            is_staff=True
        ),
        required=False,
        help_text="",
    )

    trees = filters.ModelChoiceFilter(
        queryset=TreeType.objects.all(),
        label=_("Tree"),
        help_text="",
        required=False
    )

    property__neighborhood = filters.ModelChoiceFilter(
        queryset=Neighborhood.objects.all(),
        label=_("Neighborhood"),
        help_text="",
        required=False
    )

    class Meta:
        model = Harvest
        fields = (
            'status',
            'pick_leader',
            'trees',
            'property__neighborhood',
            'season',
        )


class PropertyFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(help_text="")
    authorized = filters.BooleanFilter(help_text="")
    neighborhood = filters.ModelChoiceFilter(
        queryset=Neighborhood.objects.all(),
        label=_("Neighborhood"),
        help_text="",
        required=False
    )
    trees = filters.ModelChoiceFilter(
        queryset=TreeType.objects.all(),
        label=_("Tree"),
        help_text="",
        required=False
    )
    ladder_available = filters.BooleanFilter(help_text="")
    ladder_available_for_outside_picks = filters.BooleanFilter(help_text="")
    pending = filters.BooleanFilter(help_text="", label=_("Pending validation"))

    class Meta:
        model = Property
        fields = [
            'is_active',
            'authorized',
            'neighborhood',
            'trees',
            'ladder_available',
            'ladder_available_for_outside_picks',
            'pending',
            ]


class CommunityFilter(filters.FilterSet):

    groups = filters.ModelChoiceFilter(
        queryset=Group.objects.all(),
        label=_("Role"),
        help_text="",
        required=False
    )

    person__neighborhood = filters.ModelChoiceFilter(
        queryset=Neighborhood.objects.all(),
        label=_("Neighborhood"),
        help_text="",
        required=False
    )

    person__language = filters.ModelChoiceFilter(
        queryset=Language.objects.all(),
        label=_("Language"),
        help_text="",
        required=False
    )

    person__first_name = filters.CharFilter(
        label=_("First name"),
        method='custom_person_first_name_filter'
    )

    person__family_name = filters.CharFilter(
        label=_("Last name"),
        method='custom_person_family_name_filter'
    )

    def custom_person_first_name_filter(self, queryset, name, value):
        query = (Q(person__first_name__icontains=value))
        return queryset.filter(query)

    def custom_person_family_name_filter(self, queryset, name, value):
        query = (Q(person__family_name__icontains=value))
        return queryset.filter(query)

    class Meta:
        model = AuthUser
        fields = [
            'groups',
            'person__first_name',
            'person__family_name',
            'person__neighborhood',
            'person__language',
        ]


# FIXME: won't filter
class OrganizationFilter(filters.FilterSet):
    neighborhood = filters.ModelChoiceFilter(
        queryset=Neighborhood.objects.all(),
        label=_("Neighborhood"),
        help_text="",
        required=False
    )

    class Meta:
        model = Organization
        fields = ['neighborhood', 'is_beneficiary']


class EquipmentFilter(filters.FilterSet):
    shared = filters.BooleanFilter(help_text="")
    type = filters.ModelChoiceFilter(
        queryset=EquipmentType.objects.all(),
        label=_("Type"),
        help_text="",
        required=False
    )
    class Meta:
        model = Equipment
        fields = ['type', 'shared']


# # ADMIN filters # #

class PropertyOwnerTypeAdminFilter(SimpleListFilter):
    """Check whether owner is a Person or an Organization"""

    title = "Owner Type Filter"
    parameter_name = 'owner'
    default_value = None

    def lookups(self, request, model_admin):
        return [('0', _("Unknown")),
                ('1', _("Person")),
                ('2', _("Organization"))]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(owner__isnull=True)
        if self.value() == '1':
            return queryset.filter(owner__person__isnull=False)
        if self.value() == '2':
            return queryset.filter(owner__organization__isnull=False)
        return queryset


class PropertyHasHarvestAdminFilter(SimpleListFilter):
    """Check whether at least one harvest is associated with property"""

    title = "Had harvest Filter"
    parameter_name = 'harvest'
    default_value = None

    def lookups(self, request, model_admin):
        return [('0', 'Has harvest(s)'),
                ('1', 'No harvest yet')]

    def queryset(self, request, queryset):
        if self.value():
            test = bool(int(self.value()))
            print("test", test)
            return queryset.filter(harvests__isnull=test)
        return queryset
