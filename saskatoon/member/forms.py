# coding: utf-8
from django.utils.translation import gettext_lazy as _
from django import forms
from harvest.models import Property
from member.models import AuthUser, Person

class PersonForm(forms.ModelForm):

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

    field_order = ['first_name', 'family_name', 'email', 'language']

    def clean_email(self):
        ''' check if email address already exists'''
        email = self.cleaned_data['email']
        if AuthUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered")
        return email

    def save(self):

        # create Person instance
        instance = super(PersonForm, self).save()

        # create associated auth.user
        auth_user = AuthUser.objects.create(
                email=self.cleaned_data['email'],
                person=instance
        )
        auth_user.save()

        # associate pending_property (if any)
        pid = self.cleaned_data['pending_property_id']
        if pid:
            try:
                pending_property = Property.objects.get(id=pid)
                pending_property.owner = instance
                pending_property.save()
            except Exception as e: print(e)

        return instance
