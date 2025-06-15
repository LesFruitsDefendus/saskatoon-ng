from datetime import datetime
from dal import autocomplete
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from harvest.models import (
    Harvest,
    TreeType,
    Property,
    Equipment,
    EquipmentType
)
from member.autocomplete import AuthUserAutocomplete
from member.models import AuthUser, Neighborhood, Organization


class HarvestFilter(filters.FilterSet):
    "Harvest filter"

    class Meta:
        model = Harvest
        fields = [
            'season',
            'date',
            'status',
            'pick_leader',
            'trees',
            'ladder',
            'neighborhood',
        ]

    season = filters.ChoiceFilter(
        label=_("Season"),
        field_name='start_date',
        choices=Harvest.SEASON_CHOICES,
        lookup_expr='year',
    )

    date = filters.ChoiceFilter(
        label=_("Date"),
        choices=[
            ('next', _("Upcoming harvests only")),
            ('past', _("Past harvests only")),
            ('id', _("Lastly Created first")),
            ('old', _("Oldest to Newest"))
        ],
        help_text="",
        method='date_filter'
    )

    status = filters.ChoiceFilter(
        label=_("Status"),
        choices=list(Harvest.get_status_choices())
    )

    pick_leader = filters.ModelChoiceFilter(
        queryset=AuthUserAutocomplete.get_roles_queryset(
            AuthUser.objects.all(),
            ['pickleader', 'core']

        ),
        widget=autocomplete.ModelSelect2('pickleader-autocomplete'),
    )

    trees = filters.ModelChoiceFilter(
        label=_("Tree type"),
        queryset=TreeType.objects.all(),
        widget=autocomplete.ModelSelect2('tree-autocomplete')
    )

    ladder = filters.BooleanFilter(
        field_name='property__ladder_available',
        label=_("Ladder available"),
        help_text="",
    )

    neighborhood = filters.ModelChoiceFilter(
        field_name='property__neighborhood',
        label=_("Borough"),
        queryset=Neighborhood.objects.all(),
        widget=autocomplete.ModelSelect2('neighborhood-autocomplete'),
    )

    def date_filter(self, queryset, name, choice):
        if choice == 'next':
            return queryset.filter(start_date__gte=datetime.today())
        elif choice == 'past':
            return queryset.filter(start_date__lt=datetime.today())
        elif choice == 'id':
            return queryset.order_by('-id')
        elif choice == 'old':
            return queryset.order_by('start_date')
        return queryset


class PropertyFilter(filters.FilterSet):
    "Property filter"

    class Meta:
        model = Property
        fields = [
            'is_active',
            'pending',
            'authorized',
            'neighborhood',
            'trees',
            'ladder',
        ]

    is_active = filters.BooleanFilter(
        label=_("Active"),
        help_text=""
    )

    pending = filters.BooleanFilter(
        help_text="",
        label=_("Pending validation")
    )

    authorized = filters.ChoiceFilter(
        choices=[
            (2, _("Not yet authorized")),
            (1, _("Authorized")),
            (0, _("Unauthorized"))
        ],
        label=_("Authorized"),
        help_text="",
        method='authorized_filter'
    )

    neighborhood = filters.ModelChoiceFilter(
        queryset=Neighborhood.objects.all(),
        label=_("Borough"),
        help_text="",
        required=False
    )

    trees = filters.ModelChoiceFilter(
        queryset=TreeType.objects.all(),
        label=_("Tree"),
        help_text="",
        required=False
    )

    ladder = filters.BooleanFilter(
        field_name='ladder_available',
        label=_("Ladder available"),
        help_text="",
    )

    season = filters.ChoiceFilter(
        label=_("Harvested in"),
        field_name='season',
        choices=Harvest.SEASON_CHOICES,
        lookup_expr='year',
        method='season_filter'
    )

    def authorized_filter(self, queryset, name, choice):
        if choice == '2':
            return queryset.filter(authorized__isnull=True)
        return queryset.filter(authorized=bool(int(choice)))

    def season_filter(self, queryset, name, year):
        if year is None:
            return queryset

        harvests = Harvest.objects.filter(start_date__year=year)
        return queryset.filter(harvests__in=harvests)


class EquipmentFilter(filters.FilterSet):
    "Equipment filter"

    class Meta:
        model = Equipment
        fields = ['type', 'shared']

    shared = filters.BooleanFilter(
        help_text=""
    )

    type = filters.ModelChoiceFilter(
        queryset=EquipmentType.objects.all(),
        label=_("Type"),
        help_text="",
        required=False
    )

    equipment_point = filters.ModelChoiceFilter(
        queryset=Organization.objects.filter(is_equipment_point=True),
        label=_("Equipment Point"),
        method='equipment_point_filter'
    )

    def equipment_point_filter(self, queryset, name, value):
        return queryset.filter(owner__organization=value)
