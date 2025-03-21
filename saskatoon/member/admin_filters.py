from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from harvest.models import Property, Harvest, RequestForParticipation
from member.models import Organization, Person


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


class UserIsOnboardingAdminFilter(SimpleListFilter):
    """Checks if AuthUser is a volunteer with a password"""

    title = 'Onboarding PickLeader Filter'
    parameter_name = 'pending'
    default_value = None

    def lookups(self, request, model_admin):
        return [('1', 'volunteer w/ password')]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        group = Group.objects.get(name='volunteer')
        return queryset \
            .filter(groups__in=[group]) \
            .exclude(password__exact='') \
            .filter(has_temporary_password=True)


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
            pickers = set([r.picker for r in requests])
            users = queryset.filter(person__in=pickers)
            return users
        return queryset


class UserIsContactAdminFilter(SimpleListFilter):
    """Checks if AuthUser is contact to an Organization"""

    title = 'Contact Filter'
    parameter_name = 'contact'
    default_value = None

    def lookups(self, request, model_admin):
        return [('1', 'is contact')]

    def queryset(self, request, queryset):
        if self.value():
            organizations = Organization.objects.exclude(contact_person__isnull=True)
            contacts = set([o.contact_person for o in organizations])
            users = queryset.filter(person__in=contacts)
            return users
        return queryset


class ActorTypeAdminFilter(SimpleListFilter):
    """Checks if Actor is a Person or an Organization"""

    title = 'Type Filter'
    parameter_name = 'actor'
    default_value = None

    def lookups(self, request, model_admin):
        return [
            ('0', _("None")),
            ('1', _("Person")),
            ('2', _("Organization"))
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(person__isnull=True, organization__isnull=True)
        if self.value() == '1':
            return queryset.filter(person__isnull=False)
        if self.value() == '2':
            return queryset.filter(organization__isnull=False)
        return queryset


class PersonHasNoUserAdminFilter(SimpleListFilter):
    """Checks if a Person is associated with an AuthUser"""

    title = 'AuthUser Filter'
    parameter_name = 'user'
    default_value = None

    def lookups(self, request, model_admin):
        return [('0', 'has no auth_user')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(auth_user__isnull=True)
        return queryset


class OrganizationHasNoContactAdminFilter(SimpleListFilter):
    """Checks if a Organization has no contact"""

    title = 'Contact Filter'
    parameter_name = 'contact'
    default_value = None

    def lookups(self, request, model_admin):
        return [('0', 'has no contact')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(contact_person__isnull=True)
        return queryset
