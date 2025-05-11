from django.contrib import admin, messages
from django.db.models import Value
from django.db.models.functions import Replace
from django.urls import reverse
from django.utils.html import mark_safe

from member.models import AuthUser
from harvest.admin_filters import (
    HarvestSeasonAdminFilter,
    HarvestHasNoDateAdminFilter,
    OwnerHasNoEmailAdminFilter,
    OwnerGotAuthorizationEmailFilter,
    PropertyOwnerTypeAdminFilter,
    PropertyHasHarvestAdminFilter,
    RFPSeasonAdminFilter,
)
from harvest.admin_forms import (
    EquipmentAdminForm,
    HarvestYieldInline,
    HarvestImageInline,
    RFPPersonInline,
)
from harvest.forms import RFPForm
from harvest.models import (
    Comment,
    Equipment,
    EquipmentType,
    Harvest,
    HarvestYield,
    Property,
    PropertyImage,
    RequestForParticipation as RFP,
    TreeType,
)
from sitebase.models import Email, EmailType
from sitebase.serializers import (
    EmailPropertySerializer,
)


@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    inlines = (RFPPersonInline, HarvestYieldInline, HarvestImageInline)
    list_display = (
        'property',
        'tree_list',
        'status',
        'pick_leader',
        'start_date',
        'end_date',
        'date_created',
        'publication_date',
        'id',
    )
    list_filter = (
        HarvestSeasonAdminFilter,
        HarvestHasNoDateAdminFilter,
        'status',
    )

    @admin.display(description="Trees")
    def tree_list(self, harvest):
        return harvest.get_fruits()

    @admin.action(description="Cancel selected harvest(s)")
    def cancel_harvests(self, request, queryset):
        num_cancelled = 0
        for h in queryset:
            if h.status is not Harvest.Status.CANCELLED:
                h.status = Harvest.Status.CANCELLED
                h.save()
                num_cancelled += 1

        messages.info(request, f"Successfully cancelled {num_cancelled} harvest(s)")

    @admin.action(description="Clean harvest start/end dates")
    def clean_dates(self, request, queryset):
        num_cleaned = 0
        for h in queryset:
            save = False
            if h.start_date is None:
                h.start_date = h.date_created
                save = True
            if h.end_date is None:
                h.end_date = h.start_date
                save = True
            if save:
                h.save()
                num_cleaned += 1

        messages.info(request, f"Successfully cleaned {num_cleaned} harvest(s)")

    @admin.action(description="Clean harvest statuses")
    def clean_statuses(self, request, queryset):
        num_cleaned = 0

        for h in queryset.filter(status__isnull=False):
            status = {
                'Orphan': Harvest.Status.ORPHAN,
                'Adopted': Harvest.Status.ADOPTED,
                'To-be-confirmed': Harvest.Status.PENDING,
                'Scheduled': Harvest.Status.SCHEDULED,
                'Ready': Harvest.Status.READY,
                'Succeeded': Harvest.Status.SUCCEEDED,
                'Cancelled': Harvest.Status.CANCELLED,
            }.get(h.status)

            if status is not None:
                h.status = status
                h.save()
                num_cleaned += 1

        messages.info(request, f"Successfully cleaned {num_cleaned} harvest(s)")

    actions = [cancel_harvests, clean_dates, clean_statuses]


@admin.register(RFP)
class RequestForParticipationAdmin(admin.ModelAdmin):
    list_display = (
        'person',
        'status',
        'number_of_pickers',
        'date_created',
        'date_status_updated',
        'showed_up',
        'id',
    )
    list_filter = (
        RFPSeasonAdminFilter,
        'status',
    )
    form = RFPForm


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    form = EquipmentAdminForm


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    model = Property
    inlines = [PropertyImageInline]
    list_display = (
        'short_address',
        'owner_edit',
        'owner_type',
        'owner_phone',
        'email',
        'is_active',
        'pending',
        'harvests',
        'authorized',
        'approximative_maturity_date',
        'neighborhood',
        'city',
        'postal_code',
        'id'
    )
    list_filter = (
        PropertyOwnerTypeAdminFilter,
        PropertyHasHarvestAdminFilter,
        OwnerHasNoEmailAdminFilter,
        OwnerGotAuthorizationEmailFilter,
        'authorized',
        'is_active',
        'pending',
        'trees',
        'neighborhood',
        'city',
    )
    search_fields = (
        'street_number',
        'street',
        'postal_code_cleaned',
        'owner__person__family_name',
        'owner__person__auth_user__email',
    )
    exclude = ['longitude', 'latitude', 'geom']

    @admin.display(description="Owner type")
    def owner_type(self, _property):
        owner_subclass = _property.get_owner_subclass()
        if owner_subclass:
            return owner_subclass._meta.verbose_name.title()
        return None

    @admin.display(description="Owner")
    def owner_edit(self, _property):
        owner = _property.owner
        if not owner:
            return None
        for attr in ['person', 'organization']:
            if hasattr(owner, attr):
                obj = getattr(owner, attr)
                url = reverse(f"admin:member_{attr}_change", kwargs={'object_id': obj.pk})
                return mark_safe(f"<a href={url}>{obj}</a>")
        return None

    @admin.display(description="Owner Email")
    def email(self, _property):
        if _property.owner_email:
            return f"[U] {_property.owner_email}"  # [U]ser
        if _property.pending_contact_email:
            return f"[P] {_property.pending_contact_email}"  # [P]ending
        if _property.owner and _property.owner.is_person:
            comment_emails = ""
            for email in _property.owner.person.comment_emails:
                comment_emails += f"[C] {email} "  # [C]omments
            return comment_emails

    @admin.display(description="Harvests")
    def harvests(self, _property):
        return _property.harvests.count()

    @admin.action(description="UNAUTHORIZE selected properties ʕ•ᴥ•ʔ")
    def reset_authorize(self, request, queryset):
        """Set authorized=None to queryset"""
        queryset.update(**{'authorized': None})
        messages.info(request, "Successfully reset authorizations for this season")

    @admin.action(description="Create missing auth users using pending or comments email")
    def create_owner_user(self, request, queryset):
        """Create new AuthUser objects for owners (Persons) without email address"""

        qs = queryset.filter(owner__organization__isnull=True,
                             owner__person__isnull=False,
                             owner__person__auth_user__isnull=True)
        nb_users = 0
        for _property in qs:
            try:
                email = _property.pending_contact_email
                if not email:
                    emails = _property.owner.person.comment_emails
                    if len(emails) > 1:
                        messages.warning(
                            request,
                            f"{_property} has multiple emails in comments"
                        )
                        continue
                    elif len(emails) == 1:
                        email = emails[0]
                if email:
                    AuthUser.objects.create(email=email, person=_property.owner.person)
                    nb_users += 1
            except Exception as e:
                messages.error(request, e)

        messages.info(request, f"Successfully created {nb_users} new users!")

    @admin.action(description="Send authorization email to selected property owners")
    def send_authorization_email(self, request, queryset):
        """Send email to property owners to ask for authorization for this season"""

        num_sent = 0
        for p in queryset:
            recipient = p.email_recipient
            if recipient is None:
                messages.error(request, f"Could not find a recipient for {p}.")
                continue

            if Email.objects.create(
                recipient=recipient,
                type=EmailType.SEASON_AUTHORIZATION,
            ).send(data=dict(EmailPropertySerializer(p).data)):
                num_sent += 1
            else:
                messages.error(
                    request,
                    f"Could not send authorization email to {recipient.email}."
                )

        if num_sent > 1:
            messages.info(request, f"Sent authorization emails to {num_sent} owners!")

    actions = [reset_authorize, create_owner_user, send_authorization_email]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            postal_code_cleaned=Replace('postal_code', Value(" "), Value(""))
        )
        return queryset


@admin.register(TreeType)
class TreeTypeAdmin(admin.ModelAdmin):
    model = TreeType
    list_display = (
        'name',
        'fruit',
        'fruit_icon',
        'maturity_start',
        'maturity_end',
        'id'
    )
    search_fields = (
        'fruit_name_en',
        'fruit_name_fr',
    )


admin.site.register(EquipmentType)
admin.site.register(HarvestYield)
admin.site.register(Comment)
admin.site.register(PropertyImage)
