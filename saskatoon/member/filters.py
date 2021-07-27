from django.contrib.admin import SimpleListFilter
from member.models import AuthUser, AUTH_GROUPS, Person, Actor
from harvest.models import Property
from django.contrib.auth.models import Group

class GroupFilter(SimpleListFilter):
    title = 'Group Filter'
    parameter_name = 'group'
    default_value = None

    def lookups(self, request, model_admin):
        list_of_roles = []
        for group in Group.objects.all():
            list_of_roles.append((str(group.id), group.name))
        # return sorted(list_of_roles, key=lambda tp: tp[1])
        out = sorted(list_of_roles, key=lambda tp: tp[1])
        print("out", out)
        return out

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__in=self.value())
        return queryset

class PropertyFilter(SimpleListFilter):
    title = 'Property Filter'
    parameter_name = 'property'
    default_value = None

    def lookups(self, request, model_admin):
        return [ ('1', 'has property')]

    def queryset(self, request, queryset):
        if self.value():
            owners = [p.owner.actor_id for p in Property.objects.all() if p.owner is not None]
            persons = Person.objects.filter(actor_id__in=owners)
            users = queryset.select_related('person').filter(person__in=persons)
            return users
        return queryset
