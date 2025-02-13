from datetime import datetime
from dal import autocomplete
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework as filters
from harvest.models import (
    Harvest,
    HARVESTS_STATUS_CHOICES,
    TreeType,
    Property,
    Equipment,
    EquipmentType
)
from member.autocomplete import AuthUserAutocomplete
from member.models import AuthUser, Neighborhood, Organization

SEASON_FILTER_CHOICES = [(y, y) for y in range(datetime.now().year, 2015, -1)]


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
        choices=SEASON_FILTER_CHOICES,
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
        choices=list(HARVESTS_STATUS_CHOICES),
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
        label=_("Neighborhood"),
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

    ladder = filters.BooleanFilter(
        field_name='ladder_available',
        label=_("Ladder available"),
        help_text="",
    )

    def authorized_filter(self, queryset, name, choice):
        if choice == '2':
            return queryset.filter(authorized__isnull=True)
        return queryset.filter(authorized=bool(int(choice)))


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


# # ADMIN filters # #

class PropertyOwnerTypeAdminFilter(SimpleListFilter):
    """Check whether owner is a Person or an Organization"""

    title = "Owner Type Filter"
    parameter_name = 'owner'

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

    def lookups(self, request, model_admin):
        return [('0', 'Has harvest(s)'),
                ('1', 'No harvest yet')]

    def queryset(self, request, queryset):
        if self.value():
            is_null = bool(int(self.value()))
            return queryset.filter(harvests__isnull=is_null)
        return queryset


class OwnerHasNoEmailAdminFilter(SimpleListFilter):
    """Check if Property Owner has an email address"""

    title = 'Email Filter'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        return [('0', 'Owner has no email'),
                ('1', 'Pending email only')]

    def queryset(self, request, queryset):
        if self.value():
            qs1 = queryset.filter(
                owner__person__isnull=False,
                owner__person__auth_user__email__isnull=True
            )
            qs2 = queryset.filter(
                owner__organization__isnull=False,
                owner__organization__contact_person__auth_user__email__isnull=True
            )
            if self.value() == '0':
                return qs1 | qs2
            elif self.value() == '1':
                return (qs1 | qs2).filter(pending_contact_email__isnull=False)
        return queryset


class HarvestSeasonAdminFilter(SimpleListFilter):
    """Filter by year"""

    title = 'Season Filter'
    parameter_name = 'season'

    def lookups(self, request, model_admin):
        return SEASON_FILTER_CHOICES

    def queryset(self, request, queryset):
        return queryset.filter(start_date__year=self.value())
