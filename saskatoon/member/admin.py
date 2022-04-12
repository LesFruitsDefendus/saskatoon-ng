# coding: utf-8
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                                        ReadOnlyPasswordHashField)
from django.db.models import Value
from django.db.models.functions import Replace
from member.models import (AuthUser, Actor, OrganizationContact, Language, Person, Organization,
                           Neighborhood, City, State, Country)
from member.filters import (ActorTypeAdminFilter, UserGroupAdminFilter, UserHasPropertyAdminFilter,
                            UserHasLedPicksAdminFilter, UserHasVolunteeredAdminFilter)
from django.contrib.auth.models import Group


class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required fields,
    plus a repeated password."""

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label='Password Confirmation',
        widget=forms.PasswordInput,
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = AuthUser
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField(
        label="password",
        help_text="""Raw passwords are not stored, so there is no way to
        see this user's password, but you can change the password using
        <a href=\"../password/\"> this form</a>."""
    )

    class Meta(UserChangeForm.Meta):
        model = AuthUser
        fields = ('email', 'password', 'is_active',
                  'is_staff', 'is_superuser', 'user_permissions')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    search_fields = ('email', 'person__first_name', 'person__family_name')
    ordering = ('email', 'person')
    filter_horizontal = ('groups', 'user_permissions',)
    list_display = ('email',
                    'person',
                    'get_groups',
                    'is_staff',
                    'is_core',
                    'is_admin',
                    'is_active',
                    'id'
                    )

    @admin.display(boolean=True, description="Core")
    def is_core(self, user):
        return user.groups.filter(name="core").exists()

    @admin.display(boolean=True, description="Admin")
    def is_admin(self, user):
        return user.groups.filter(name="admin").exists()

    @admin.display(description="Group(s)")
    def get_groups(self, user):
        return ' + '.join([g.name for g in user.groups.all()])

    list_filter = (UserGroupAdminFilter,
                   UserHasPropertyAdminFilter,
                   UserHasLedPicksAdminFilter,
                   UserHasVolunteeredAdminFilter,
                   'is_staff',
                   'is_superuser',
                   'is_active'
                   )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                    'person'
                )
            }
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups'
                )
            }
        ),
    )

    add_fieldsets = (
        (
            None, {
                'classes': 'wide',
                'fields': (
                    'email',
                    'password1',
                    'password2',
                    'is_staff',
                    'is_superuser',
                    'groups'
                )
            }
        ),
    )

    # ACTIONS
    @admin.action(description="Deactivate account for selected User(s)")
    def deactivate_account(self, request, queryset):
        for u in queryset:
            if u.is_superuser:
                messages.add_message(request, messages.ERROR,
                                     f"Cannot deactivate account for superuser {u}")
                continue
            u.is_active = False
            u.save()

    @admin.action(description="Add staff status to selected User(s)")
    def add_to_staff(self, request, queryset):
        queryset.update(**{'is_staff': True})

    @admin.action(description="Remove staff status from selected User(s)")
    def remove_from_staff(self, request, queryset):
        queryset.update(**{'is_staff': False})

    @admin.action(description="Remove superuser status from selected User(s)")
    def remove_from_superuser(self, request, queryset):
        queryset.update(**{'is_superuser': False})

    @admin.action(description="Clear groups for selected User(s)")
    def clear_groups(self, request, queryset):
        for u in queryset:
            u.groups.clear()
            u.is_superuser = False
            u.is_staff = False
            u.save()

    def add_to_group(self, user, name):
        """helper function for add_to_<group> actions"""
        group, __ = Group.objects.get_or_create(name=name)
        user.groups.add(group)

    @admin.action(description="Add selected User(s) to admin group")
    def add_to_admin(self, request, queryset):
        for u in queryset:
            self.add_to_group(u, 'admin')
            u.is_superuser = True
            u.is_staff = True
            u.save()

    @admin.action(description="Add selected User(s) to core group")
    def add_to_core(self, request, queryset):
        for u in queryset:
            self.add_to_group(u, 'core')
            u.is_staff = True
            u.save()

    @admin.action(description="Add selected User(s) to pickleader group")
    def add_to_pickleader(self, request, queryset):
        for u in queryset:
            self.add_to_group(u, 'pickleader')
            u.is_staff = True
            u.save()

    @admin.action(description="Add selected User(s) to volunteer group")
    def add_to_volunteer(self, request, queryset):
        for u in queryset:
            self.add_to_group(u, 'volunteer')

    @admin.action(description="Add selected User(s) to owner group")
    def add_to_owner(self, request, queryset):
        for u in queryset:
            self.add_to_group(u, 'owner')

    actions = [
        deactivate_account,
        remove_from_staff,
        remove_from_superuser,
        add_to_staff,
        clear_groups,
        add_to_admin,
        add_to_core,
        add_to_pickleader,
        add_to_volunteer,
        add_to_owner,
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'phone',
        'email',
        'street_number',
        'street',
        'neighborhood',
        'postal_code',
        'newsletter_subscription',
        'language',
    )
    list_filter = (
        'neighborhood',
        'city',
        'language',
        'newsletter_subscription',
    )
    search_fields = (
        'first_name',
        'family_name',
        'phone',
        'postal_code_cleaned',
        'auth_user__email',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            postal_code_cleaned=Replace('postal_code', Value(" "), Value(""))
        )
        return queryset


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type', 'pk')
    list_filter = (ActorTypeAdminFilter,)

    @admin.display(description="Type")
    def type(self, actor):
        if actor.is_person:
            return Person._meta.verbose_name.title()
        if actor.is_organization:
            return Organization._meta.verbose_name.title()
        return None


admin.site.register(Language)
admin.site.register(Organization)
admin.site.register(OrganizationContact)
admin.site.register(Neighborhood)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)
