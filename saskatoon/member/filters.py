from django.contrib.admin import SimpleListFilter
from member.models import Person #Actor, AuthUser, AUTH_GROUPS
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from harvest.models import Property, Harvest, RequestForParticipation


# # ADMIN filters # #

class UserGroupAdminFilter(SimpleListFilter):
    """Checks if AuthUser belongs to Group"""

    title = 'Group Filter'
    parameter_name = 'group'
    default_value = None

    def lookups(self, request, model_admin):
        list_of_roles = [('0', '__none__')]
        for group in Group.objects.all():
            list_of_roles.append((str(group.id), group.name))
        return sorted(list_of_roles, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(groups__isnull=True)
        elif self.value():
            return queryset.filter(groups__in=self.value())
        return queryset


class UserHasPropertyAdminFilter(SimpleListFilter):
    """Checks if AuthUser is a property owner"""

    title = 'Property Filter'
    parameter_name = 'property'
    default_value = None

    def lookups(self, request, model_admin):
        return [('1', 'has a property')]

    def queryset(self, request, queryset):
        if self.value():
            properties = Property.objects.select_related('owner').filter(owner__isnull=False)
            owners = set([p.owner.actor_id for p in properties])
            persons = Person.objects.select_related('actor_id').filter(actor_id__in=owners)
            users = queryset.select_related('person').filter(person__in=persons)
            return users
        return queryset


class UserHasLedPicksAdminFilter(SimpleListFilter):
    """Checks if AuthUser has led harvests"""

    title = 'Pick-Leader Filter'
    parameter_name = 'leader'
    default_value = None

    def lookups(self, request, model_admin):
        return [('1', 'has led pick(s)')]

    def queryset(self, request, queryset):
        if self.value():
            harvests = Harvest.objects.filter(pick_leader__isnull=False)
            leaders = set([h.pick_leader.person for h in harvests])
            users = queryset.filter(person__in=leaders)
            return users
        return queryset


class UserHasVolunteeredAdminFilter(SimpleListFilter):
    """Checks if AuthUser has volunteered"""

    title = 'Volunteer Filter'
    parameter_name = 'picker'
    default_value = None

    def lookups(self, request, model_admin):
        return [('1', 'has volunteered')]

    def queryset(self, request, queryset):
        if self.value():
            requests = RequestForParticipation.objects.filter(is_accepted=True)
            pickers = [r.picker for r in requests]
            users = queryset.filter(person__in=pickers)
            return users
        return queryset


class ActorTypeAdminFilter(SimpleListFilter):
    """Checks if Actor is a Person or an Organization"""

    title = 'Type Filter'
    parameter_name = 'actor'
    default_value = None

    def lookups(self, request, model_admin):
        return [('0', _("None")),
                ('1', _("Person")),
                ('2', _("Organization"))]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(person__isnull=True, organization__isnull=True)
        if self.value() == '1':
            return queryset.filter(person__isnull=False)
        if self.value() == '2':
            return queryset.filter(organization__isnull=False)
        return queryset
