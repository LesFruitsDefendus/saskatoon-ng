from dal import autocomplete
from .models import AuthUser, Person, Actor
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q


class PersonAutocomplete(autocomplete.Select2QuerySetView):
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
    ''' Pick Leader + Core Members'''
    def __init__(self):
        super(PickLeaderAutocomplete, self).__init__(['pickleader', 'core'])


class OwnerAutocomplete(PersonAutocomplete):
    ''' Property owner '''
    def __init__(self):
        super(OwnerAutocomplete, self).__init__(['owner'])


class ContactAutocomplete(PersonAutocomplete):
    ''' Organization contact person'''
    def __init__(self):
        super(ContactAutocomplete, self).__init__(['contact'])


class ActorAutocomplete(autocomplete.Select2QuerySetView):
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
