from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from typing import Optional

from sitebase.models import Email


class EmailIsDuplicateAdminFilter(SimpleListFilter):
    """Checks if Email object is identical to previous one"""

    title = 'Duplicate Filter'
    parameter_name = 'dup'
    default_value: Optional[Email] = None

    def lookups(self, request, model_admin):
        return [
            ('yes', _('Duplicates')),
            ('no', _('Originals')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            duplicates = [e.id for e in queryset if e.is_duplicate]
            if self.value() == 'yes':
                return queryset.filter(id__in=duplicates)
            if self.value() == 'no':
                return queryset.exclude(id__in=duplicates)

        return queryset
