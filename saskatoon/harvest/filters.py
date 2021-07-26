from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from harvest.models import Harvest, HARVESTS_STATUS_CHOICES, TreeType, Property, Equipment,  EquipmentType
from member.models import Language, AuthUser, Neighborhood, Organization
from django.db.models.query_utils import Q
from django.contrib.auth.models import Group

FILTER_HARVEST_CHOICES = list(HARVESTS_STATUS_CHOICES)

class HarvestFilter(filters.FilterSet):
    seasons = []
    for y in Harvest.objects.all():
        if y.start_date is not None:
            t_seasons = (
                    y.start_date.strftime("%Y"),
                    y.start_date.strftime("%Y")
                )
            seasons.append(t_seasons)
    seasons = list(set(seasons))
    seasons = sorted(seasons, key=lambda tup: tup[1])

    start_date = filters.ChoiceFilter(
        choices=seasons,
        label=_("Season"),
        lookup_expr='year',
        help_text="",
    )

    status = filters.ChoiceFilter(
        choices=FILTER_HARVEST_CHOICES,
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
        fields = {
        'status': ['exact'],
        'pick_leader': ['exact'],
        'trees': ['exact'],
        'property__neighborhood': ['exact'],
        'start_date': ['exact'],
        }


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
            'person__property',
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
