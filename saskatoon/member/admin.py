import csv
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.db.models import Value
from django.db.models.functions import Replace
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.html import mark_safe
from logging import getLogger
from typing import Optional

from member.admin_filters import (
    ActorTypeAdminFilter,
    OrganizationHasNoContactAdminFilter,
    PersonHasNoUserAdminFilter,
    UserGroupAdminFilter,
    UserHasPropertyAdminFilter,
    UserHasLedPicksAdminFilter,
    UserHasVolunteeredAdminFilter,
    UserIsContactAdminFilter,
    UserIsOnboardingAdminFilter,
)
from member.admin_forms import (
    AuthUserChangeAdminForm,
    AuthUserCreationAdminForm,
    OrganizationEquipmentInlineAdminForm,
    PendingPickLeaderInlineAdminForm,
)
from member.models import (
    Actor,
    AuthUser,
    City,
    Country,
    Neighborhood,
    Onboarding,
    Organization,
    Person,
    State,
)
from member.utils import reset_password
from saskatoon.settings import EMAIL_LIST_OUTPUT
from sitebase.models import Email, EmailType

logger = getLogger('saskatoon')


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    form = AuthUserChangeAdminForm
    add_form = AuthUserCreationAdminForm
    search_fields = ('email', 'person__first_name', 'person__family_name')
    ordering = ('email', 'person', 'date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)
    list_display = (
        'email',
        'person',
        'get_groups',
        'is_staff',
        'is_core',
        'is_admin',
        'is_active',
        'has_password',
        'agreed_terms',
        'id',
        'date_joined',
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

    list_filter = (
        UserGroupAdminFilter,
        UserHasPropertyAdminFilter,
        UserHasLedPicksAdminFilter,
        UserHasVolunteeredAdminFilter,
        UserIsContactAdminFilter,
        UserIsOnboardingAdminFilter,
        'is_staff',
        'is_superuser',
        'is_active',
        'agreed_terms',
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'password',
                    'has_temporary_password',
                    'person',
                    'agreed_terms',
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
                    'has_temporary_password',
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

    @admin.action(description="Reset selected User(s)'s T&C agreement")
    def reset_agreed_terms(self, request, queryset):
        queryset.update(agreed_terms=False)

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
        reset_agreed_terms,
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
    inlines = [OrganizationEquipmentInlineAdminForm]
    list_display = ('__str__', 'contact', 'is_beneficiary', 'is_equipment_point', 'pk')
    list_filter = (OrganizationHasNoContactAdminFilter,)

    fieldsets = (
        (
            'Info',
            {
                'fields': (
                    'civil_name',
                    'description',
                    'phone',
                    'contact_person',
                    'street_number',
                    'street',
                    'complement',
                    'postal_code',
                    'neighborhood',
                    'city',
                    'state',
                    'country',
                    )
            },
        ),
        (
            'Fruit donations',
            {
                'fields': (
                    'is_beneficiary',
                    'beneficiary_description',
                )
            },
        ),
        (
            'Equipment Point',
            {
                'fields': (
                    'is_equipment_point',
                    'equipment_description',
                    )
            }
        ),
    )

    @admin.display(description="Contact Person")
    def contact(self, org):
        if org.contact_person:
            obj = org.contact_person
            url = reverse('admin:member_person_change', kwargs={'object_id': obj.pk})
            return mark_safe(f"<a href={url}>{obj}</a>")
        return None

    def save_related(self, request, form, formsets, change):
        """Ensure is_equipment_point box was not mistakenly left checked/unchecked"""

        super().save_related(request, form, formsets, change)

        org = Organization.objects.get(actor_id=form.instance.actor_id)
        if not org.equipment.exists():
            org.is_equipment_point = False
            org.save()
            messages.add_message(
                request, messages.WARNING,
                f"{org} cannot be listed as an Equipment Point because no equipment \
                is currently registered for this Organization."
            )
        elif not org.is_equipment_point:
            messages.add_message(
                request, messages.WARNING,
                f"{org} has equipment but is not listed as an Equipment Point. \
                Only leave the \"Is Equipment Point\" box unchecked if the equipment \
                is not currently available."
            )


admin.site.register(Neighborhood)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)


@admin.register(Onboarding)
class OnboardingAdmin(admin.ModelAdmin):
    inlines = [PendingPickLeaderInlineAdminForm]
    list_display = ('name', 'datetime', 'user_count', 'all_sent', 'id')

    def save_model(self, request, obj, form, change):
        """Make sure all_sent is False if users get added later on"""
        if obj.all_sent and obj.persons.filter(auth_user__password='').exists():
            obj.all_sent = False
            messages.add_message(
                request,
                messages.WARNING,
                f"Some users in {obj} were not yet invited."
            )
        super().save_model(request, obj, form, change)

    @admin.action(description="Send registration invite to selected group(s)")
    def send_invite(self, request, queryset):
        num_sent = 0
        for o in queryset:
            o.all_sent = True
            o.log += "\n[{}]".format(tz.localtime(tz.now()).strftime("%B %d, %Y @ %-I:%M %p"))
            for p in o.persons.filter(auth_user__password=''):
                m = Email.objects.create(recipient=p, type=EmailType.REGISTRATION)

                if m.send(data={'password': reset_password(p.auth_user)}) == 1:
                    num_sent += 1
                    o.log += f"\n\t> OK {p.auth_user.email}"
                else:
                    p.auth_user.password = ''
                    p.auth_user.has_temporary_password = False
                    p.auth_user.save()
                    o.all_sent = False
                    o.log += f"\n\t> FAIL {p.auth_user.email}"
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Could not send Registration Invite to {p.auth_user.email}"
                    )

            if o.all_sent:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Successfully sent Registration Invite to {num_sent} users"
                )
            o.save()

    actions = [
        send_invite
    ]
