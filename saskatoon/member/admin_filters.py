from datetime import datetime, timedelta
from typing import Optional

from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from harvest.models import Property, RequestForParticipation
from member.models import Actor, AuthUser, Organization, Person


class UserGroupAdminFilter(SimpleListFilter):
    """Checks if AuthUser belongs to Group"""

    title = 'Group Filter'
    parameter_name = 'group'
    default_value: Optional[Group] = None

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


class UserHasPasswordAdminFilter(SimpleListFilter):
    """Checks if AuthUser has a password"""

    title = 'Password Filter'
    parameter_name = 'pwd'
    default_value: Optional[AuthUser] = None

    def lookups(self, request, model_admin):
        return [
            ('0', 'has no password'),
            ('1', 'has password'),
            ('2', 'has temporary password'),
            ('3', 'onboarding pickleader'),
            ('4', 'active pickleader'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == '0':
            return queryset.filter(password__exact='')

        if self.value() == '1':
            return queryset.exclude(password__exact='')

        if self.value() == '2':
            return queryset.exclude(password__exact='').filter(has_temporary_password=True)

        if self.value() == '3':
            group = Group.objects.get(name='volunteer')
            return queryset.exclude(password__exact='').filter(
                groups__in=[group], is_active=True, has_temporary_password=True
            )

        if self.value() == '4':
            group = Group.objects.get(name='pickleader')
            return queryset.exclude(password__exact='').filter(
                groups__in=[group], is_active=True, has_temporary_password=False
            )


class UserHasSignedInAdminFilter(SimpleListFilter):
    """Checks if AuthUser has signed in recently"""

    title = 'Login Filter'
    parameter_name = 'login'
    default_value: Optional[AuthUser] = None

    CURRENT_SEASON = datetime.now().year - 1

    def lookups(self, request, model_admin):
        return [
            ('current', 'has signed-in this season'),
            ('last', 'has signed-in last season'),
            ('not', 'has not signed-in in 2 years'),
            ('never', 'has never signed-in'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 'current':
            return queryset.filter(last_login__year__gte=self.CURRENT_SEASON)

        if self.value() == 'last':
            return queryset.filter(
                last_login__year__gte=self.CURRENT_SEASON - 1,
                last_login__year__lt=self.CURRENT_SEASON,
            )

        if self.value() == 'not':
            return queryset.filter(last_login__lt=datetime.now() - timedelta(weeks=105))

        if self.value() == 'never':
            return queryset.filter(last_login__isnull=True)


class UserHasPropertyAdminFilter(SimpleListFilter):
    """Checks if AuthUser is a property owner"""

    title = 'Property Filter'
    parameter_name = 'property'
    default_value: Optional[Property] = None

    def lookups(self, request, model_admin):
        return [
            ('all', 'has property'),
            ('active', 'has active property'),
            ('inactive', 'has only inactive property'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value not in ('all', 'active', 'inactive'):
            return queryset

        properties = Property.objects.filter(owner__isnull=False)
        if value == 'active':
            properties = properties.filter(is_active=True)
        elif value == 'inactive':
            properties = properties.filter(is_active=False).exclude(
                owner__properties__is_active=True
            )

        persons = Person.objects.filter(actor_id__in=properties.values('owner_id'))
        return queryset.select_related('person').filter(person__in=persons)


class UserHasLedPicksAdminFilter(SimpleListFilter):
    """Checks if AuthUser has led harvests"""

    title = 'Pick-Leader Filter'
    parameter_name = 'leader'
    default_value: Optional[AuthUser] = None

    def lookups(self, request, model_admin):
        return [('1', 'has led pick(s)')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(harvests__isnull=False).distinct()
        return queryset


class UserHasVolunteeredAdminFilter(SimpleListFilter):
    """Checks if AuthUser has volunteered"""

    title = 'Volunteer Filter'
    parameter_name = 'picker'
    default_value: Optional[AuthUser] = None

    def lookups(self, request, model_admin):
        return [('1', 'has volunteered')]

    def queryset(self, request, queryset):
        if self.value():
            pickers = Person.objects.filter(
                requests__status=RequestForParticipation.Status.ACCEPTED
            )
            users = queryset.filter(person__in=pickers)
            return users
        return queryset


class UserIsContactAdminFilter(SimpleListFilter):
    """Checks if AuthUser is contact to an Organization"""

    title = 'Contact Filter'
    parameter_name = 'contact'
    default_value: Optional[AuthUser] = None

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
    default_value: Optional[Actor] = None

    def lookups(self, request, model_admin):
        return [('0', _("None")), ('1', _("Person")), ('2', _("Organization"))]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(person__isnull=True, organization__isnull=True)
        if self.value() == '1':
            return queryset.filter(person__isnull=False)
        if self.value() == '2':
            return queryset.filter(organization__isnull=False)
        return queryset


class UserHasNoPersonAdminFilter(SimpleListFilter):
    """Checks if a AuthUser is associated with a Person"""

    title = 'Has No Person Filter'
    parameter_name = 'user'
    default_value: Optional[AuthUser] = None

    def lookups(self, request, model_admin):
        return [('0', 'has no person')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(person__isnull=True)
        return queryset


class PersonHasNoUserAdminFilter(SimpleListFilter):
    """Checks if a Person is associated with an AuthUser"""

    title = 'Has No AuthUser Filter'
    parameter_name = 'user'
    default_value: Optional[Person] = None

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
    default_value: Optional[Person] = None

    def lookups(self, request, model_admin):
        return [('0', 'has no contact')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(contact_person__isnull=True)
        return queryset


class OrganizationHasLocationAdminFilter(SimpleListFilter):
    """Check whether Organization has geom field set"""

    title = "Has Location Filter"
    parameter_name = 'geom'

    def lookups(self, request, model_admin):
        return [('0', 'No location set'), ('1', 'Has GPS coordinates')]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.exclude(geom__isnull=bool(int(value)))
        return queryset
