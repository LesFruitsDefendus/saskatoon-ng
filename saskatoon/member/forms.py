# coding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django import forms
from dal import autocomplete
from harvest.models import Property
from member.models import AuthUser, Person, Organization, AUTH_GROUPS, STAFF_GROUPS
from django.contrib.auth.models import Group


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

def set_person_roles(person, roles):
    ''' updates auth_user groups
        :param person: Person instance
        :param roles: list of group names (see AUTH_GROUPS)
    '''
    auth_user = AuthUser.objects.get(person=person)
    auth_user.groups.clear()
    for role in roles:
        group, __ =  Group.objects.get_or_create(name=role)
        auth_user.groups.add(group)

    auth_user.is_staff = any([r in STAFF_GROUPS for r in roles])
    auth_user.save()

def validate_email(email):
    ''' check if a user with same email address is already registered'''
    if AuthUser.objects.filter(email=email).exists():
        raise forms.ValidationError(
            _("ERROR: email address < {} > is already registered!").format(email)
        )
    return email

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

    roles =  forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=AUTH_GROUPS,
        required=True
    )

    field_order = ['roles', 'first_name', 'family_name', 'email', 'language']

    def clean_email(self):
        return validate_email(self.cleaned_data['email'])

    def save(self):
        # create Person instance
        instance = super(PersonCreateForm, self).save()

        # create associated auth.user
        auth_user = AuthUser.objects.create(
                email=self.cleaned_data['email'],
                person=instance
        )
        auth_user.save()

        set_person_roles(instance, self.cleaned_data['roles'])

        # associate pending_property (if any)
        pid = self.cleaned_data['pending_property_id']
        if pid:
            try:
                pending_property = Property.objects.get(id=pid)
                pending_property.owner = instance
                pending_property.save()
            except Exception as e: print(e)

        return instance

class PersonUpdateForm(forms.ModelForm):

    class Meta:
        model = Person
        exclude = ['redmine_contact_id', 'longitude', 'latitude']

    roles =  forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=AUTH_GROUPS,
        required=True
    )

    field_order = ['roles', 'first_name', 'family_name', 'language']

    def __init__(self, *args, **kwargs):
        super(PersonUpdateForm, self).__init__(*args, **kwargs)
        try:
            auth_user = AuthUser.objects.get(person=self.instance)
            self.initial['roles'] = [g for g in auth_user.groups.all()]
        except ObjectDoesNotExist:
            self.fields.pop('roles')
            # TODO: log this warning in a file
            print("WARNING!: Person {} has no associated Auth.User!".format(self.instance))

    def save(self):
        super(PersonUpdateForm, self).save()
        try:
            set_person_roles(self.instance, self.cleaned_data['roles'])
        except KeyError:
            pass
        return self.instance


class OrganizationCreateForm(forms.ModelForm):

    class Meta:
        model = Organization
        exclude = ['redmine_contact_id', 'longitude', 'latitude']
        labels = {
            'is_beneficiary': _("Beneficiary organization"),
            'contact_person_role': _("Position/Role"),
        }


    contact_person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        label=_("Select Person"),
        widget=autocomplete.ModelSelect2('contact-autocomplete'),
        required=False,
        # help_text="FDODFlasdflasfjaslf"
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
        auth_user.save()

        set_person_roles(person, ['contact'])

        # # associate Contact to Organization
        instance.contact_person = person
        instance.save()

        return instance


class OrganizationUpdateForm(forms.ModelForm):

    class Meta:
        model = Organization
        exclude = ['redmine_contact_id', 'longitude', 'latitude']
        labels = {
            'is_beneficiary': _("Beneficiary organization"),
            'contact_person_role': _("Contact Position/Role"),
        }

        widgets = {
            'contact_person': autocomplete.ModelSelect2(
               'contact-autocomplete'
            ),
        }
