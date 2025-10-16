from django import forms
from django.contrib import admin

from member.models import AuthUser, Person
from harvest.models import Equipment

from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    ReadOnlyPasswordHashField,
)


class AuthUserCreationAdminForm(UserCreationForm[AuthUser]):
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

    class Meta:
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


class AuthUserChangeAdminForm(UserChangeForm[AuthUser]):
    password = ReadOnlyPasswordHashField(
        help_text="""Raw passwords are not stored, so there is no way to
        see this user's password, but you can change the password using
        <a href=\"../password/\"> this form</a>."""
    )

    class Meta:
        model = AuthUser
        exclude = ('date_joined',)

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class PendingPickLeaderAdminForm(forms.ModelForm[Person]):
    """A simple form to onboard new pickleaders"""

    class Meta:
        model = Person
        fields = ['email', 'first_name', 'family_name', 'phone', 'language']

    email = forms.EmailField(
        label="email",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_user = None
        if self.instance.onboarding_id is not None:
            self.auth_user = AuthUser.objects.get(person=self.instance)
            self.initial['email'] = self.auth_user.email

    def save(self, commit=True):
        self.instance = super().save(commit=False)
        data = self.cleaned_data
        person = Person.objects.filter(auth_user__email=data.get('email')).first()
        if person:
            for key in ['first_name', 'family_name', 'phone']:
                setattr(person, key, data.get(key))
            person.onboarding = self.instance.onboarding
            person.save()
            self.instance.pk = person.pk
            return self.instance

        return super().save(commit)


class PendingPickLeaderInlineAdminFormSet(forms.models.BaseInlineFormSet):

    def get_emails(self):
        return dict([(f.instance.pk, f.cleaned_data.get('email'))
                     for f in self.forms if f.instance.pk is not None])

    def clean(self):
        email_list = list(self.get_emails().values())
        if len(email_list) != len(set(email_list)):
            raise forms.ValidationError("Duplicate emails found.")

    def save_new_objects(self, commit=True):
        saved_instances = super().save_new_objects(commit)
        for person in [p for p in saved_instances if p is not None]:
            email = self.get_emails().get(person.pk)
            user, _ = AuthUser.objects.get_or_create(email=email, person=person)

            # PickLeaders don't get assigned the 'pickleader' role until
            # they have read and agreed to the privacy policy
            user.add_role('volunteer')

        return saved_instances

    def save_existing_objects(self, commit=True):
        saved_instances = super().save_existing_objects(commit)
        for i, person in enumerate(saved_instances):
            user = AuthUser.objects.get(person=person)
            user.email = self.get_emails().get(person.pk)
            user.save()

        return saved_instances


class PendingPickLeaderInlineAdminForm(admin.TabularInline):
    model = Person
    fields = ['email', 'first_name', 'family_name', 'phone', 'language']
    form = PendingPickLeaderAdminForm
    formset = PendingPickLeaderInlineAdminFormSet
    extra = 9


class OrganizationEquipmentInlineAdminForm(admin.TabularInline):
    model = Equipment
    fields = ['type', 'description', 'count']
    extra = 2
