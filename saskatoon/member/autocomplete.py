from dal import autocomplete
from django.contrib.auth.models import Group
from django.db.models import Q, QuerySet
from typeguard import typechecked
from datetime import timedelta

from .models import AuthUser, Organization, Person, Actor, Neighborhood
from harvest.utils import available_equipment_points

# WARNING: Don't forget to filter out the results depending on the user's role!


@typechecked
def _is_not_authenticated(autocomplete: autocomplete.Select2QuerySetView) -> bool:
    """Helper function to check if users are authenticated.
    Request is not always present in unit tests so we need to check for it"""

    has_request = hasattr(autocomplete, 'request')

    return (has_request and not autocomplete.request.user.is_authenticated) or not has_request


@typechecked
class PersonAutocomplete(autocomplete.Select2QuerySetView):
    """Person autocomplete with optional role filter"""

    def __init__(self, roles=[]) -> None:
        self.roles = roles

    def get_queryset(self) -> QuerySet[Person]:
        if _is_not_authenticated(self):
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


@typechecked
class ContactAutocomplete(PersonAutocomplete):
    """Persons with contact role (aka Organizations' contact persons)"""

    def __init__(self) -> None:
        super().__init__(['contact'])


@typechecked
class AuthUserAutocomplete(autocomplete.Select2QuerySetView):
    """AuthUser autocomplete with optional role filter"""

    def __init__(self, roles=[]) -> None:
        self.roles = roles

    @staticmethod
    def get_roles_queryset(queryset, roles) -> QuerySet[Group]:
        groups = Group.objects.filter(name__in=roles).values('id')
        return queryset.filter(groups__in=groups).distinct()

    """
    I (Patrick) could not get this method to typecheck properly, mypy does not recognize
    AuthUser, it calls it AbstractBaseUser and the qs = self.get_roles_queryset line
    causes since it's already initiated as a QuerySet[AbstractBaseUser], but I'm
    not sure if the Q invocations after are used on qs in the case of self.q, so I've
    left it untyped for now.
    """
    def get_queryset(self):
        if _is_not_authenticated(self):
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


@typechecked
class PickLeaderAutocomplete(AuthUserAutocomplete):
    """AuthUser autocomplete for core members and pickleaders"""

    def __init__(self) -> None:
        super().__init__(['pickleader', 'core'])


@typechecked
class ActorAutocomplete(autocomplete.Select2QuerySetView):
    """Actor autocomplete"""

    def get_queryset(self) -> QuerySet[Actor]:
        if _is_not_authenticated(self):
            return Actor.objects.none()

        qs = Actor.objects.all()

        if self.q:
            q0 = Q(person__first_name__icontains=self.q)
            q1 = Q(person__family_name__icontains=self.q)
            q2 = Q(organization__civil_name__icontains=self.q)
            qs = qs.filter(q0 | q1 | q2)

        return qs.distinct()


@typechecked
class OwnerAutocomplete(autocomplete.Select2QuerySetView):
    """Organizations + Persons with owner role"""

    def get_queryset(self) -> QuerySet[Actor]:
        if _is_not_authenticated(self):
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


@typechecked
class EquipmentPointAutocomplete(autocomplete.Select2QuerySetView):
    """Organizations that are Equipment Points"""

    def get_queryset(self) -> QuerySet[Organization]:
        qs = Organization.objects.none()

        if _is_not_authenticated(self):
            return qs

        start = self.forwarded.get('start_date', None)
        end = self.forwarded.get('end_date', None)

        if start and end:
            qs = available_equipment_points(start, end, timedelta(hours=1))

        return qs.distinct()


@typechecked
class NeighborhoodAutocomplete(autocomplete.Select2QuerySetView):
    """Neighborhoods (aka Boroughs)"""

    def get_queryset(self) -> QuerySet[Neighborhood]:
        if _is_not_authenticated(self):
            return Neighborhood.objects.none()

        return Neighborhood.objects.all()
