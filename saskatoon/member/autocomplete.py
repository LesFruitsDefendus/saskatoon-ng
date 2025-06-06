from dal import autocomplete
from django.contrib.auth.models import Group
from django.db.models.query_utils import Q
from .models import AuthUser, Organization, Person, Actor, Neighborhood

# WARNING: Don't forget to filter out the results depending on the user's role!


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    """Person autocomplete with optional role filter"""

    def __init__(self, roles=[]):
        self.roles = roles

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.roles:
            groups = [Group.objects.get(name=role).id for role in self.roles]
            qs = qs.filter(auth_user__groups__in=groups)

        if self.q:
            q0 = Q(first_name__icontains=self.q)
            q1 = Q(family_name__icontains=self.q)
            qs = qs.filter(q0 | q1)

        return qs.distinct()


class ContactAutocomplete(PersonAutocomplete):
    """Persons with contact role (aka Organizations' contact persons)"""

    def __init__(self):
        super().__init__(['contact'])


class AuthUserAutocomplete(autocomplete.Select2QuerySetView):
    """AuthUser autocomplete with optional role filter"""

    def __init__(self, roles=[]):
        self.roles = roles

    @staticmethod
    def get_roles_queryset(queryset, roles):
        groups = Group.objects.filter(name__in=roles).values('id')
        return queryset.filter(groups__in=groups)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return AuthUser.objects.none()

        qs = AuthUser.objects.all()

        if self.roles:
            qs = self.get_roles_queryset(qs, self.roles)

        if self.q:
            q0 = Q(email__icontains=self.q)
            q1 = Q(person__first_name__icontains=self.q)
            q2 = Q(person__family_name__icontains=self.q)
            qs = qs.filter(q0 | q1 | q2)

        return qs.distinct()


class PickLeaderAutocomplete(AuthUserAutocomplete):
    """AuthUser autocomplete for core members and pickleaders"""

    def __init__(self):
        super().__init__(['pickleader', 'core'])


class ActorAutocomplete(autocomplete.Select2QuerySetView):
    """Actor autocomplete"""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Actor.objects.none()

        qs = Actor.objects.all()

        if self.q:
            q0 = Q(person__first_name__icontains=self.q)
            q1 = Q(person__family_name__icontains=self.q)
            q2 = Q(organization__civil_name__icontains=self.q)
            qs = qs.filter(q0 | q1 | q2)

        return qs.distinct()


class OwnerAutocomplete(autocomplete.Select2QuerySetView):
    """Organizations + Persons with owner role"""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Actor.objects.none()

        f1 = Q(organization__isnull=False)
        f2 = Q(person__auth_user__groups__in=[Group.objects.get(name='owner')])
        qs = Actor.objects.filter(f1 | f2)

        if self.q:
            q0 = Q(person__first_name__icontains=self.q)
            q1 = Q(person__family_name__icontains=self.q)
            q2 = Q(organization__civil_name__icontains=self.q)
            qs = qs.filter(q0 | q1 | q2)

        return qs.distinct()


class EquipmentPointAutocomplete(autocomplete.Select2QuerySetView):
    """Organizations that are Equipment Points"""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Organization.objects.none()

        qs = Organization.objects.filter(is_equipment_point=True)

        if self.q:
            qs = qs.filter(organization__civil_name__icontains=self.q)

        return qs.distinct()


class NeighborhoodAutocomplete(autocomplete.Select2QuerySetView):
    """Neighborhoods (aka Boroughs)"""

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Neighborhood.objects.none()

        return Neighborhood.objects.all()
