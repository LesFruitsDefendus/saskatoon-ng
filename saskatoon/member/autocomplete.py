from django.contrib.auth.models import Group, AbstractBaseUser
from django.db.models import Q, QuerySet
from typeguard import typechecked
from logging import getLogger
from django.conf import settings

from harvest.models import Harvest
from member.models import AuthUser, Organization, Person, Actor, Neighborhood
from member.utils import available_equipment_points
from saskatoon.autocomplete import Autocomplete
from sitebase.utils import parse_naive_datetime

# WARNING: Don't forget to filter out the results depending on the user's role!

logger = getLogger("saskatoon")


@typechecked
class PersonAutocomplete(Autocomplete):
    """Person autocomplete with optional role filter"""

    def __init__(self, roles=[]) -> None:
        self.roles = roles

    def get_queryset(self) -> QuerySet[Person]:
        if not self.is_authenticated():
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
class AuthUserAutocomplete(Autocomplete):
    """AuthUser autocomplete with optional role filter"""

    def __init__(self, roles=[]) -> None:
        self.roles = roles

    @staticmethod
    def get_roles_queryset(queryset, roles) -> QuerySet[AbstractBaseUser]:
        groups = Group.objects.filter(name__in=roles).values('id')
        return queryset.filter(groups__in=groups).distinct()

    def get_queryset(self) -> QuerySet[AbstractBaseUser]:
        if not self.is_authenticated():
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
class ActorAutocomplete(Autocomplete):
    """Actor autocomplete"""

    def get_queryset(self) -> QuerySet[Actor]:
        if not self.is_authenticated():
            return Actor.objects.none()

        qs = Actor.objects.all()

        if self.q:
            q0 = Q(person__first_name__icontains=self.q)
            q1 = Q(person__family_name__icontains=self.q)
            q2 = Q(organization__civil_name__icontains=self.q)
            qs = qs.filter(q0 | q1 | q2)

        return qs.distinct()


@typechecked
class OwnerAutocomplete(Autocomplete):
    """Organizations + Persons with owner role"""

    def get_queryset(self) -> QuerySet[Actor]:
        if not self.is_authenticated():
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
class EquipmentPointAutocomplete(Autocomplete):
    """Organizations that are Equipment Points"""

    def get_queryset(self) -> QuerySet[Organization]:
        none = Organization.objects.none()

        if not self.is_authenticated():
            return none

        start_str = self.forwarded.get('start_date', "")
        end_str = self.forwarded.get('end_date', "")
        if start_str == "" and end_str == "":
            return Organization.objects.filter(is_equipment_point=True)

        if start_str == "" or end_str == "":
            return none

        start = parse_naive_datetime(start_str, settings.AUTOCOMPLETE_DATETIME_FORMAT)
        end = parse_naive_datetime(end_str, settings.AUTOCOMPLETE_DATETIME_FORMAT)
        if start is None or end is None or start > end:
            return none

        try:
            harvest_id = int(self.forwarded.get('id', ""))
            harvest = Harvest.objects.get(pk=harvest_id)

        except (Harvest.DoesNotExist, ValueError):
            harvest = None

        return available_equipment_points(start, end, harvest).distinct()


@typechecked
class NeighborhoodAutocomplete(Autocomplete):
    """Neighborhoods (aka Boroughs)"""

    def get_queryset(self) -> QuerySet[Neighborhood]:
        if not self.is_authenticated():
            return Neighborhood.objects.none()

        return Neighborhood.objects.all()
