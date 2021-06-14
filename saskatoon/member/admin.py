# coding: utf-8

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ( UserCreationForm, UserChangeForm,
        ReadOnlyPasswordHashField )
from django import forms

from member.models import (AuthUser, Actor, Language, Person, Organization, Neighborhood, City, State, Country)

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


class AuthUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    search_fields = ('email', 'person__first_name', 'person__family_name')
    ordering = ('email', 'person')
    filter_horizontal = ('groups', 'user_permissions',)
    list_display = ('email', 'person', 'is_staff', 'is_core', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


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


admin.site.register(AuthUser, AuthUserAdmin)
# admin.site.register(Notification)
admin.site.register(Actor)
admin.site.register(Language)
admin.site.register(Person)
admin.site.register(Organization)
admin.site.register(Neighborhood)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)
