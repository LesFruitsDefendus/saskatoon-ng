# coding: utf-8
import csv
from typing import Optional
from django import forms
from django.core.mail import EmailMessage
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (UserCreationForm, UserChangeForm,
                                        ReadOnlyPasswordHashField)
from django.contrib.auth.models import Group
from django.db.models import Value
from django.db.models.functions import Replace
from django.forms.models import BaseInlineFormSet
from django.urls import reverse
from django.utils.html import mark_safe
from member.models import (AuthUser, Actor, Language, Onboarding, Person,
                           Organization, Neighborhood, City, State, Country)
from member.filters import (ActorTypeAdminFilter, UserGroupAdminFilter,
                            UserHasPropertyAdminFilter, UserHasLedPicksAdminFilter,
                            UserHasVolunteeredAdminFilter, UserIsContactAdminFilter,
                            UserIsPendingValidation,
                            PersonHasNoUserAdminFilter, OrganizationHasNoContactAdminFilter)
from member.utils import send_reset_password_email

from saskatoon.settings import EMAIL_LIST_OUTPUT


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
    ordering = ('email', 'person', 'date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)
    list_display = ('email',
                    'person',
                    'get_groups',
                    'is_staff',
                    'is_core',
                    'is_admin',
                    'is_active',
                    'id',
                    'date_joined',
                    'has_password',
                    'last_login',
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

    @admin.display(boolean=True, description="Password")
    def has_password(self, user):
        return user.password != ''

    list_filter = (UserGroupAdminFilter,
                   UserHasPropertyAdminFilter,
                   UserHasLedPicksAdminFilter,
                   UserHasVolunteeredAdminFilter,
                   UserIsContactAdminFilter,
                   UserIsPendingValidation,
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

    @admin.action(description="Add selected User(s) to contact group")
    def add_to_contact(self, request, queryset):
        for u in queryset:
            self.add_to_group(u, 'contact')

    @admin.action(description="Export email list with selected User(s)")
    def export_emails(self, request, queryset):
        contacts = queryset.values_list(
            'person__first_name',
            'person__family_name',
            'email'
        ).order_by('person__first_name')

        def clean_column(col: Optional[str]) -> str:
            if col is None:
                return 'NONE'
            return col.replace(',', '')

        with open(EMAIL_LIST_OUTPUT, 'w', newline='') as tmpFile:
            wr = csv.writer(tmpFile, delimiter=',', quoting=csv.QUOTE_NONE)
            wr.writerow(['FirstName', 'LastName', 'Email'])
            for contact in contacts:
                row = [clean_column(col) for col in contact]
                wr.writerow(row)

        mailto = request.user.email
        with open(EMAIL_LIST_OUTPUT, 'rb') as csvFile:
            try:
                email = EmailMessage("Saskatoon Email List", "", None, [mailto])
                email.attach('Saskatoon_EmailList.csv', csvFile.read(), 'text/csv')
                email.send()
                messages.add_message(
                    request, messages.SUCCESS,
                    f"Email list successfully sent to {mailto}"
                )
            except Exception as e:
                messages.add_message(
                    request, messages.ERROR,
                    f"Something went wrong: {e}"
                )

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
        add_to_contact,
        export_emails,
    ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'authuser',
        'phone',
        'street_number',
        'street',
        'neighborhood',
        'postal_code',
        'newsletter_subscription',
        'language',
        'pk'
    )
    list_filter = (
        PersonHasNoUserAdminFilter,
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

    @admin.display(description="AuthUser")
    def authuser(self, person):
        try:
            user = person.auth_user
            url = reverse('admin:member_authuser_change', kwargs={'object_id': user.id})
            return mark_safe(f"<a href={url}>{user.email}</a>")
        except AuthUser.DoesNotExist:
            return None

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
        for attr in ['person', 'organization']:
            if hasattr(actor, attr):
                obj = getattr(actor, attr)
                url = reverse(f"admin:member_{attr}_change", kwargs={'object_id': obj.pk})
                return mark_safe(f"<a href={url}>{attr.capitalize()}</a>")
        return None


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contact', 'pk')
    list_filter = (OrganizationHasNoContactAdminFilter,)

    @admin.display(description="Contact Person")
    def contact(self, org):
        if org.contact_person:
            obj = org.contact_person
            url = reverse('admin:member_person_change', kwargs={'object_id': obj.pk})
            return mark_safe(f"<a href={url}>{obj}</a>")
        return None


admin.site.register(Language)
admin.site.register(Neighborhood)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)


class PendingPickLeaderForm(forms.ModelForm):
    """A simple form to onboard new pickleaders"""

    class Meta:
        model = Person
        fields = ['email', 'first_name', 'family_name', 'phone', 'language']

    email = forms.EmailField(
        label="email",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(PendingPickLeaderForm, self).__init__(*args, **kwargs)
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


class PendingPickLeaderInlineFormSet(BaseInlineFormSet):

    def get_emails(self):
        forms = [f for f in self.forms if f.instance.pk is not None]
        return dict([(f.instance.pk, f.cleaned_data.get('email')) for f in forms])

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


class PendingPickLeaderInlineForm(admin.TabularInline):
    model = Person
    fields = ['email', 'first_name', 'family_name', 'phone', 'language']
    form = PendingPickLeaderForm
    formset = PendingPickLeaderInlineFormSet
    extra = 9


@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    inlines = [PendingPickLeaderInlineForm]
    list_display = ('__str__', 'user_count', 'invite_sent', 'id')

    @admin.action(description="Send registration invite to selected group(s)")
    def send_invite(self, request, queryset):
        persons = []
        for o in queryset:
            persons += o.persons.all()

        subject = "Les Fruits Défendus - Saskatoon Registration"
        num_sent = 0

        for p in persons:
            mailto = p.auth_user.email
            message = "Hi " + p.first_name + ",\n\n\
You are receiving this email following your recent participation to the Pickleader training \
organized by Les Fruits Défendus. You can now log into the Saskatoon harvest management \
platform using your email address and the temporary password provided below.\n\n\
Login page: https://saskatoon.lesfruitsdefendus.org/accounts/login/\n\
Email address: " + mailto + "\n\
Temporary password: {password}\n\n\
Thanks for supporting your community!\n\n--\n\n\
Bonjour " + p.first_name + ",\n\n\
Vous recevez ce courriel suite à votre récente participation à la formation de chef.fe the cueillette \
organisée par Les Fruits Défendus. Vous pouvez désormais vous connecter sur la plateforme de \
gestion Saskatoon en utilisant votre adresse courriel et le mot de passe temporaire fourni plus bas.\n\n\
Page de connexion: https://saskatoon.lesfruitsdefendus.org/accounts/login/\n\
Adresse électronique: " + mailto + "\n\
Mot de passe temporaire: {password}\n\n\
Merci de soutenir votre communauté!\n\n--\n\n\
Les Fruits Défendus"

            if send_reset_password_email(p.auth_user, subject, message):
                num_sent += 1
            else:
                messages.add_message(request, messages.ERROR,
                                     f"Failed sending Registration Invite to {p.auth_user.email}")

        if num_sent == len(persons):
            messages.add_message(request, messages.SUCCESS,
                                f"Successfully sent Registration Invite to {num_sent} users")

    actions = [
        send_invite
    ]
