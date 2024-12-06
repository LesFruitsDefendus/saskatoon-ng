from dal import autocomplete
from harvest.models import Equipment
from member.utils import get_equipment_points_available_in_daterange
from .models import AuthUser, Organization, Person, Actor
from django.contrib.auth.models import Group
from django.db.models.query_utils import Q


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    """Person autocomplete with optional role filter"""

    def __init__(self, roles=[]):
        self.roles = roles

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
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

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return AuthUser.objects.none()

        qs = AuthUser.objects.all()

        if self.roles:
            groups = [Group.objects.get(name=role).id for role in self.roles]
            qs = qs.filter(groups__in=groups)

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
        # Don't forget to filter out results depending on the visitor !
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
        # Don't forget to filter out results depending on the visitor !
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
            qs = qs.filter(civil_name__icontains=self.q)

        start_date = self.forwarded.get('start_date', None)
        end_date = self.forwarded.get('end_date', None)
        if start_date is not None and end_date is not None:
            qs = qs.filter(actor_id__in=get_equipment_points_available_in_daterange(start_date, end_date))
            qs = Equipment.objects.filter(actor_id__in=qs)

        # currently, queryset shows all available equipment
        # since we are replacing labels with the eq_point org name, this means multiple copies of each
        # distinct() with field params only available on Postgres. 
        #TODO:find workaround to remove entries with duplicate equipment.owner fields for mySQL
        return qs.distinct()


class EquipmentByEquipmentPointAutocomplete(autocomplete.Select2QuerySetView):
    """
    Equipment labelled by Equipment Points that own them 
        - returns equipment queryset, but labels are the names of owner organizations/equipment points
        - optionally filters by availability within a forwarded start/end date range
    """

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Equipment.objects.none()

        f1 = Q(organization__isnull=False)
        f2 = Q(organization__is_equipment_point=True)
        qs = Actor.objects.filter(f1 & f2)

        if self.q:
            q0 = Q(organization__civil_name__icontains=self.q)
            qs = qs.filter(q0)

        start_date = self.forwarded.get('start_date', None)
        end_date = self.forwarded.get('end_date', None)
        if start_date is not None and end_date is not None:
            qs = qs.filter(organization__in=get_equipment_points_available_in_daterange(start_date, end_date))
            qs = Equipment.objects.all().filter(owner__in=qs)

        # currently, queryset shows all available equipment
        # since we are replacing labels with the eq_point org name, this means multiple copies of each
        # distinct() with field params only available on Postgres. 
        #TODO:find workaround to remove entries with duplicate equipment.owner fields for mySQL
        return qs.distinct()

    def get_result_label(self, equipment):
        return equipment.owner.get_organization().name

    def get_selected_result_label(self, equipment):
        return equipment.owner.get_organization().name
