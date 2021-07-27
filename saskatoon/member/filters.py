from django.contrib.admin import SimpleListFilter
from member.models import AuthUser, AUTH_GROUPS, Person, Actor
from harvest.models import Property, Harvest
from django.contrib.auth.models import Group

class GroupFilter(SimpleListFilter):
    title = 'Group Filter'
    parameter_name = 'group'
    default_value = None

    def lookups(self, request, model_admin):
        list_of_roles = []
        for group in Group.objects.all():
            list_of_roles.append((str(group.id), group.name))
        return sorted(list_of_roles, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__in=self.value())
        return queryset

class PropertyFilter(SimpleListFilter):
    title = 'Property Filter'
    parameter_name = 'property'
    default_value = None

    def lookups(self, request, model_admin):
        return [ ('1', 'has a property')]

    def queryset(self, request, queryset):
        if self.value():
            properties = Property.objects.select_related('owner').filter(owner__isnull=False)
            owners = set([p.owner.actor_id for p in properties])
            persons = Person.objects.select_related('actor_id').filter(actor_id__in=owners)
            users = queryset.select_related('person').filter(person__in=persons)
            return users
        return queryset

class PickLeaderFilter(SimpleListFilter):
    title = 'Pick-Leader Filter'
    parameter_name = 'leader'
    default_value = None

    def lookups(self, request, model_admin):
        return [ ('1', 'has led pick(s)')]

    def queryset(self, request, queryset):
        if self.value():
            harvests = Harvest.objects.filter(pick_leader__isnull=False)
            leaders = set([h.pick_leader.person for h in harvests])
            users = queryset.filter(person__in=leaders)
            return users
        return queryset
