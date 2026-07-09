from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from typing import Optional

from sitebase.models import Email


class EmailIsDuplicateAdminFilter(SimpleListFilter):
    """Checks if Email object is identical to previous one"""

    title = 'Duplicate Filter'
    parameter_name = 'login'
    default_value: Optional[Email] = None

    def lookups(self, request, model_admin):
        return [
            ('dup', _('Duplicates')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'dup':
            duplicates = [e.id for e in queryset if e.is_duplicate]
            print("DUPLICATES!", duplicates)
            return queryset.filter(id__in=duplicates)

        return queryset
