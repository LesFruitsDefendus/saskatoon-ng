# coding: utf-8
# from leaflet.admin import LeafletGeoAdmin  # type: ignore
from django.contrib import admin, messages
from django.db.models import Value
from django.db.models.functions import Replace
from django.urls import reverse
from django.utils.html import mark_safe
from django import forms
from dal import autocomplete
from harvest.models import (Property, Harvest, RequestForParticipation, TreeType,
                            Equipment, EquipmentType, HarvestYield, Comment,
                            PropertyImage, HarvestImage)
from harvest.filters import (PropertyOwnerTypeAdminFilter, PropertyHasHarvestAdminFilter,
                             HarvestSeasonAdminFilter, OwnerHasNoEmailAdminFilter)
from harvest.forms import (RFPForm, HarvestYieldForm, EquipmentAdminForm)
from member.models import AuthUser


class PersonInline(admin.TabularInline):
    model = RequestForParticipation
    verbose_name = "Cueilleurs pour cette récolte"
    verbose_name_plural = "Cueilleurs pour cette récolte"
    form = RFPForm
    exclude = ['creation_date', 'confirmation_date']
    extra = 3


class HarvestYieldInline(admin.TabularInline):
    model = HarvestYield
    form = HarvestYieldForm


class HarvestImageInline(admin.TabularInline):
    model = HarvestImage
    extra = 3


@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    model = Harvest
    inlines = (PersonInline, HarvestYieldInline, HarvestImageInline)
    list_display = (
        'property',
        'tree_list',
        'status',
        'pick_leader',
        'creation_date',
        'publication_date',
        'start_date',
        'id',
    )
    list_filter = (
        HarvestSeasonAdminFilter,
        'status',
    )

    @admin.display(description="Trees")
    def tree_list(self, harvest):
        return harvest.get_fruits()

    @admin.action(description="Cancel selected harvest(s)")
    def cancel_harvests(self, request, queryset):
        num_cancelled = 0
        for h in queryset:
            if h.status != 'Cancelled':
                h.status = 'Cancelled'
                h.save()
                num_cancelled += 1

        messages.add_message(request, messages.SUCCESS,
                             f"Successfully cancelled {num_cancelled} harvest(s)")

    actions = [cancel_harvests]


@admin.register(RequestForParticipation)
class RequestForParticipationAdmin(admin.ModelAdmin):
    form = RFPForm


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    form = EquipmentAdminForm


class EquipmentAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(EquipmentAdminForm, self).clean()
        bool1 = bool(self.cleaned_data['property'])
        bool2 = bool(self.cleaned_data['owner'])
        if not (bool1 != bool2):
            raise forms.ValidationError(
                'Fill in one of the two fields: property or owner.'
            )
        return cleaned_data

    class Meta:
        model = Equipment
        widgets = {
            'property': autocomplete.ModelSelect2(
                'property-autocomplete'
            ),
            'owner': autocomplete.ModelSelect2(
                'actor-autocomplete'
            ),
        }

        fields = '__all__'


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3


@admin.register(Property)
# class PropertyAdmin(LeafletGeoAdmin):
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

    @admin.action(description="De-authorized selected properties")
    def reset_authorize(self, request, queryset):
        """Set authorized=None to queryset"""
        queryset.update(**{'authorized': None})
        messages.add_message(request, messages.SUCCESS,
                             "Successfully reset authorizations for this season")

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
                        messages.add_message(request, messages.WARNING,
                                f"{_property} has multiple emails in comments")
                        continue
                    elif len(emails) == 1:
                        email = emails[0]
                if email:
                    AuthUser.objects.create(email=email, person=_property.owner.person)
                    nb_users += 1
            except Exception as e:
                messages.add_message(request, messages.ERROR, e)

        messages.add_message(request, messages.SUCCESS,
                             f"Successfully created {nb_users} new users!")

    actions = [reset_authorize, create_owner_user]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            postal_code_cleaned=Replace('postal_code', Value(" "), Value(""))
        )
        return queryset


admin.site.register(TreeType)
admin.site.register(EquipmentType)
admin.site.register(HarvestYield)
admin.site.register(Comment)
admin.site.register(PropertyImage)
