from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from harvest.models import Harvest, HARVESTS_STATUS_CHOICES, TreeType, Property
from member.models import Language, AuthUser, Neighborhood
from django.db.models.query_utils import Q


FILTER_HARVEST_CHOICES = list(HARVESTS_STATUS_CHOICES)
#FILTER_HARVEST_CHOICES.insert(0, ('', '---------'))

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
        fields = ['is_active', 'authorized', 'pending', 'neighborhood', 'trees', 'ladder_available', 'ladder_available_for_outside_picks']

class CommunityFilter(filters.FilterSet):
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

    person__first_name = filters.CharFilter(label="First name", method='custom_person_first_name_filter')
    person__family_name = filters.CharFilter(label="Family name", method='custom_person_family_name_filter')
    person__property = filters.BooleanFilter(label="Has property", method='custom_person_property_filter')


    def custom_person_first_name_filter(self, queryset, name, value):
        query = (Q(person__first_name__icontains=value))
        return queryset.filter(query)

    def custom_person_family_name_filter(self, queryset, name, value):
        query = (Q(person__family_name__icontains=value))
        return queryset.filter(query)

    def custom_person_property_filter(self, queryset, name, value):
        #TODO: fix this epic workaround
        if value is True:
            query = (Q(person__property__isnull=False))
        elif value is False:
            query = (Q(person__property__isnull=True))
        return queryset.filter(query)

    class Meta:
        model = AuthUser
        fields = [
        'person__neighborhood',
        'person__language',
        'person__first_name',
        'person__family_name',
        'person__property',
        ]
