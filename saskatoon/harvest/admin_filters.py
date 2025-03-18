from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _

from harvest.models import Harvest


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
    """Filter harvests by year"""

    title = 'Season Filter'
    parameter_name = 'season'

    def lookups(self, request, model_admin):
        return Harvest.SEASON_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(start_date__year=self.value())
        return queryset


class RFPSeasonAdminFilter(HarvestSeasonAdminFilter):
    """Filter requests by year"""

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(harvest__start_date__year=self.value())
        return queryset
