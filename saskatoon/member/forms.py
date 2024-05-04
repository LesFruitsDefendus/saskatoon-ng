# coding: utf-8
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import forms as auth_forms
from django.forms.widgets import PasswordInput

from dal import autocomplete
from logging import getLogger
from harvest.models import Property
from member.models import AuthUser, Person, Organization, AUTH_GROUPS, STAFF_GROUPS
from member.validators import validate_email

logger = getLogger('saskatoon')


class PersonCreateForm(forms.ModelForm):

    class Meta:
        model = Person
        exclude = ['redmine_contact_id', 'longitude', 'latitude']

    email = forms.EmailField(
        label=_("Email"),
        required=True
    )

    # when registering owner based off pending property info
    pending_property_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False
    )

    roles = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=AUTH_GROUPS,
        required=True
    )

    field_order = ['roles', 'first_name', 'family_name', 'email', 'language']

    def clean(self):
        cleaned_data = super().clean()
        validate_email(cleaned_data['email'])

    def save(self):
        # create Person instance
        instance = super(PersonCreateForm, self).save()

        # create associated auth.user
        auth_user = AuthUser.objects.create(
                email=self.cleaned_data['email'],
                person=instance
        )
        roles = self.cleaned_data['roles']
        auth_user.set_roles(roles)

        # associate pending_property (if any)
        pid = self.cleaned_data['pending_property_id']
        if pid and 'owner' in roles:
            try:
                pending_property = Property.objects.get(id=pid)
                pending_property.owner = instance
                pending_property.save()
            except Exception as e:
                logger.error("%s: %s", type(e), str(e))

        return instance


class PersonUpdateForm(forms.ModelForm):

    class Meta:
        model = Person
        exclude = ['redmine_contact_id', 'longitude', 'latitude']

    roles = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=AUTH_GROUPS,
        required=False
    )

    email = forms.EmailField(
        label=_("Email"),
        required=False
    )

    field_order = ['roles', 'email', 'first_name', 'family_name', 'language']

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop('request_user')
        super(PersonUpdateForm, self).__init__(*args, **kwargs)

        self.auth_user = None
        if not request_user.has_perm('member.change_authuser'):
            self.fields.pop('email')
            self.fields.pop('roles')
        else:
            try:
                self.auth_user = AuthUser.objects.get(person=self.instance)
                self.initial['roles'] = [g for g in self.auth_user.groups.all()]
                self.initial['email'] = self.auth_user.email
            except ObjectDoesNotExist:
                logger.warning("Person {} has no associated Auth.User!".format(self.instance))

    def clean(self):
        super().clean()
        email = self.cleaned_data.get('email', None)
        validate_email(email, self.auth_user)

        roles = self.cleaned_data.get('roles', None)
        if email and not roles:
            raise forms.ValidationError(
                _("Please assign at least one role to the user"))
        elif roles and not email:
            raise forms.ValidationError(
                _("An email address is required to assign a role to the user"))

    def save(self):
        instance = super().save()
        email = self.cleaned_data.get('email', None)
        roles = self.cleaned_data.get('roles', None)
        if email and roles:
            if not self.auth_user:
                self.auth_user = AuthUser.objects.create(person=instance, email=email)
            self.auth_user.email = email
            self.auth_user.set_roles(roles)  # calls auth_user.save()


class OnboardingPersonUpdateForm(forms.ModelForm):

    class Meta:
        model = Person
        exclude = ['redmine_contact_id', 'longitude', 'latitude']

    def save(self):
        super().save()
        self.instance.auth_user.add_role('pickleader')


class OrganizationForm(forms.ModelForm):

    class Meta:
        model = Organization
        exclude = ['redmine_contact_id', 'longitude', 'latitude']
        labels = {
            'is_beneficiary': _("Beneficiary organization"),
            'contact_person_role': _("Contact Position/Role"),
        }

        widgets = {
            'contact_person': autocomplete.ModelSelect2('contact-autocomplete'),
        }


class OrganizationCreateForm(OrganizationForm):

    contact_person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        label=_("Select Person"),
        widget=autocomplete.ModelSelect2('contact-autocomplete'),
        required=False,
    )

    create_new_person = forms.BooleanField(
        label=_("&nbsp;Register new contact person"),
        required=False
    )

    contact_first_name = forms.CharField(
        label=_("First Name"),
        help_text=_("This field is required"),
        required=False
    )

    contact_last_name = forms.CharField(
        label=_("Last Name"),
        required=False
    )

    contact_email = forms.EmailField(
        label=_("Email"),
        help_text=_("This field is required"),
        required=False
    )

    contact_phone = forms.CharField(
        label=_("Phone"),
        required=False
    )

    def clean(self):
        data = super().clean()
        person = data['contact_person']
        if not person:
            if data['contact_email'] and data['contact_first_name']:
                validate_email(data['contact_email'])
            else:
                raise forms.ValidationError(
                    _("ERROR: You must either select a Contact \
                    Person or create a new one and provide their personal information"))
        return data


    def save(self):
        # # create Organization instance
        instance = super(OrganizationCreateForm, self).save()

        # # create Contact Person/AuthUser
        person = Person.objects.create(
            first_name=self.cleaned_data['contact_first_name'],
            family_name=self.cleaned_data['contact_last_name'],
            phone=self.cleaned_data['contact_phone'])
        person.save()

        auth_user = AuthUser.objects.create(
            email=self.cleaned_data['contact_email'],
            person=person)
        auth_user.set_roles(['contact'])

        # # associate Contact to Organization
        instance.contact_person = person
        instance.save()

        return instance


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    error_messages = {
        **auth_forms.PasswordChangeForm.error_messages,
        'password_unchanged': _("Your new password must be different than your old password."),
    }

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        # replace widgets with placeholder values to fit Notika theme
        self.fields['old_password'].widget = PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password', 'placeholder': 'Old password', 'autofocus': True })
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'New password'})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'Confirm password'})

    def clean_new_password1(self):
        """
        Validate that the new_password does not match old_password.
        """
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password1')
        if old_password and new_password:
            if old_password == new_password:
                raise ValidationError(
                    self.error_messages['password_unchanged'],
                    code='password_unchanged',
                )
        return new_password

    def save(self, commit=True):
        instance = super().save(False)
        instance.has_temporary_password = False
        instance.save()
        return instance
