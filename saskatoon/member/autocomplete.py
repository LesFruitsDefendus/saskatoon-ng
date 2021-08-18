from dal import autocomplete
from .models import AuthUser, Person, Actor
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def __init__(self, role=None):
        self.role = role

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.all()

        if self.role:
            group, __ =  Group.objects.get_or_create(name=self.role)
            qs = qs.filter(auth_user__groups=group)

        if self.q:
            qs = qs.filter(first_name__icontains=self.q)

        return qs

class PickLeaderAutocomplete(PersonAutocomplete):
    ''' Pick Leader '''
    def __init__(self):
        super(PickLeaderAutocomplete, self).__init__('pickleader')

class OwnerAutocomplete(PersonAutocomplete):
    ''' Property owner '''
    def __init__(self):
        super(OwnerAutocomplete, self).__init__('owner')

class ContactAutocomplete(PersonAutocomplete):
    ''' Organization contact person'''
    def __init__(self):
        super(ContactAutocomplete, self).__init__('contact')


class ActorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Actor.objects.none()

        qs = Actor.objects.all()
        list_actor = []

        if self.q:
            first_name = qs.filter(
                person__first_name__icontains=self.q
            )
            family_name = qs.filter(
                person__family_name__icontains=self.q
            )
            civil_name = qs.filter(
                organization__civil_name__icontains=self.q
            )

            for actor in first_name:
                if actor not in list_actor:
                    list_actor.append(actor)

            for actor in family_name:
                if actor not in list_actor:
                    list_actor.append(actor)

            for actor in civil_name:
                if actor not in list_actor:
                    list_actor.append(actor)

        if not list_actor:
            list_actor = qs

        return list_actor
