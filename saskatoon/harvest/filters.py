from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from harvest.models import Harvest, HARVESTS_STATUS_CHOICES, TreeType, Property
from member.models import AuthUser, Neighborhood

FILTER_HARVEST_CHOICES = list(HARVESTS_STATUS_CHOICES)
FILTER_HARVEST_CHOICES.insert(0, ('', '---------'))

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
