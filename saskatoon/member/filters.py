from dal import autocomplete
from django.contrib.auth.models import Group
from django.db.models.query_utils import Q
from django.db.models import Count
from django import forms
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from typeguard import typechecked
from datetime import datetime, timezone, timedelta

from sitebase.utils import parse_naive_datetime
from member.utils import available_equipment_points
from member.models import AuthUser, Organization, Person, Neighborhood
from harvest.models import EquipmentType, Equipment, Harvest, RequestForParticipation


class CommunityFilter(filters.FilterSet):
    "Community filter"

    class Meta:
        model = AuthUser
        fields = ['role', 'neighborhood', 'language', 'season']

    role = filters.MultipleChoiceFilter(
        choices=AuthUser.GROUPS,
        label=_("Role(s)"),
        widget=forms.CheckboxSelectMultiple,
        method='role_filter',
    )

    neighborhood = filters.ModelChoiceFilter(
        field_name='person__neighborhood',
        queryset=Neighborhood.objects.all(),
        label=_("Borough"),
    )

    language = filters.ChoiceFilter(
        field_name='person__language',
        choices=Person.Language.choices,
        label=_("Language"),
    )

    season = filters.ChoiceFilter(
        label=_("Active in"),
        field_name='season',
        choices=Harvest.SEASON_CHOICES,
        lookup_expr='year',
        method='season_filter',
    )

    sort = filters.ChoiceFilter(
        label=_("Sort by"),
        choices=[
            ('leads', _("Most harvests led")),
            ('picks', _("Most participations")),
        ],
        help_text="",
        method='sort_filter',
    )

    def role_filter(self, queryset, name, roles):
        groups = Group.objects.filter(name__in=roles)
        return queryset.filter(groups__in=groups)

    def person_first_name_filter(self, queryset, name, value):
        query = Q(person__first_name__icontains=value)
        return queryset.filter(query)

    def person_family_name_filter(self, queryset, name, value):
        query = Q(person__family_name__icontains=value)
        return queryset.filter(query)

    def season_filter(self, queryset, name, year):
        if year is None:
            return queryset

        harvests = Harvest.objects.filter(
            start_date__year=year,
            status__in=[
                Harvest.Status.ADOPTED,
                Harvest.Status.SCHEDULED,
                Harvest.Status.SUCCEEDED,
            ],
        )
        leaders = Q(harvests__in=harvests)
        owners = Q(person__properties__harvests__in=harvests)
        pickers = Q(person__requests__harvest__in=harvests)
        return queryset.filter(leaders | owners | pickers).distinct()

    def sort_filter(self, queryset, name, choice):
        if choice == 'leads':
            return queryset.annotate(
                leads=Count(
                    'harvests',
                    filter=Q(
                        harvests__status__in=[
                            Harvest.Status.SUCCEEDED,
                            Harvest.Status.SCHEDULED,
                        ]
                    ),
                )
            ).order_by('-leads')
        elif choice == 'picks':
            return queryset.annotate(
                picks=Count(
                    'person__requests',
                    filter=Q(
                        person__requests__status=RequestForParticipation.Status.ACCEPTED,
                        person__requests__harvest__status=Harvest.Status.SUCCEEDED,
                    ),
                )
            ).order_by('-picks')
        else:
            return queryset


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
        method='type_filter',
    )

    neighborhood = filters.ModelChoiceFilter(
        label=_("Borough"),
        queryset=Neighborhood.objects.all(),
        widget=autocomplete.ModelSelect2('neighborhood-autocomplete'),
    )

    def type_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(is_beneficiary=True)
        if value == '2':
            return queryset.filter(is_equipment_point=True)
        return queryset


@typechecked
class EquipmentPointFilter(filters.FilterSet):
    """Equipment Point filter"""

    class Meta:
        model = Organization
        fields = [
            'beneficiary',
            'equipment_type',
            'neighborhood',
        ]

    beneficiary = filters.BooleanFilter(
        field_name='is_beneficiary',
        label=_("Beneficiary"),
        widget=forms.CheckboxInput,
        method='beneficiary_filter',
    )

    neighborhood = filters.ModelChoiceFilter(
        label=_("Borough"),
        queryset=Neighborhood.objects.all(),
        widget=autocomplete.ModelSelect2('neighborhood-autocomplete'),
    )

    equipment_type = filters.ModelChoiceFilter(
        label=_("Equipment Type"),
        queryset=EquipmentType.objects.all(),
        method='equipment_type_filter',
    )

    def beneficiary_filter(self, queryset, name, value):
        if value:
            return queryset.filter(is_beneficiary=True)
        return queryset

    def equipment_type_filter(self, queryset, name, value):
        if value:
            equipments = Equipment.objects.filter(type=value)
            return queryset.filter(equipment__in=equipments).distinct()
        return queryset

    status = filters.ChoiceFilter(
        label=_("Status"),
        choices=[
            ('1', _('Is Reserved')),
            ('2', _('Is Available')),
        ],
        method='status_filter',
    )

    status = filters.ChoiceFilter(
        label=_("Status"),
        choices=[
            ('1', _('Is Reserved')),
            ('2', _('Is Available')),
        ],
        method='status_filter',
    )

    start = filters.DateTimeFilter(label=_("From"), method='status_filter', default="yyyy-mm-dd")

    end = filters.DateTimeFilter(label=_("To"), method='status_filter', default="yyyy-mm-dd")

    def status_filter(self, queryset, name, value):
        start = parse_naive_datetime(self.data.get('start', ""), "%Y-%m-%d") or datetime.now(
            timezone.utc
        )
        end = (
            parse_naive_datetime(self.data.get('end', ""), "%Y-%m-%d")
            or timedelta(days=365) + start
        )
        status = self.data.get('status', None)

        if status == '1' and start < end:
            available = available_equipment_points(start, end, None).values('actor_id')
            return queryset.exclude(pk__in=available).filter(is_equipment_point=True)

        if status == '2' and start < end:
            return available_equipment_points(start, end, None)

        return queryset.filter(is_equipment_point=True)
