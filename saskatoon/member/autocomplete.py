from dal import autocomplete
from .models import Person, Actor  #AuthUser
from django.contrib.auth.models import Group
#from django.contrib.auth.decorators import login_required
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

        return qs


class PickLeaderAutocomplete(PersonAutocomplete):
    """Pick Leaders + Core Members"""

    def __init__(self):
        super(PickLeaderAutocomplete, self).__init__(['pickleader', 'core'])


class ContactAutocomplete(PersonAutocomplete):
    """Persons with contact role (aka Organizations' contact persons)"""

    def __init__(self):
        super(ContactAutocomplete, self).__init__(['contact'])


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

        return qs


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

        return qs
