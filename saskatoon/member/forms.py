# coding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django import forms
from dal import autocomplete
from harvest.models import Property
from member.models import AuthUser, Person, Organization, AUTH_GROUPS, STAFF_GROUPS
from django.contrib.auth.models import Group

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
        ''' check if email address already exists'''
        email = self.cleaned_data['email']
        if AuthUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered")
        return email

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
            'is_beneficiary': "Beneficiary organization",
        }

        widgets = {
            'contact_person': autocomplete.ModelSelect2(
               'actor-autocomplete'
            ),
        }

    # field_order = ['civil_name', 'is_beneficiary', 'description']

    # is_beneficiary = forms.BooleanField(
    #     label=_("Beneficiary organization"),
    #     required=False
    # )


    # def clean_email(self):
    #     ''' check if email address already exists'''
    #     email = self.cleaned_data['email']
    #     if AuthUser.objects.filter(email=email).exists():
    #         raise forms.ValidationError("This email address is already registered")
    #     return email

    # def save(self):

        # # create Person instance
        # instance = super(PersonCreateForm, self).save()

        # # create associated auth.user
        # auth_user = AuthUser.objects.create(
        #         email=self.cleaned_data['email'],
        #         person=instance
        # )
        # auth_user.save()
        # set_person_roles(instance, self.cleaned_data['roles'])

        # # associate pending_property (if any)
        # pid = self.cleaned_data['pending_property_id']
        # if pid:
        #     try:
        #         pending_property = Property.objects.get(id=pid)
        #         pending_property.owner = instance
        #         pending_property.save()
        #     except Exception as e: print(e)
        # return instance
