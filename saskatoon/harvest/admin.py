#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Models registration.
"""

from leaflet.admin import LeafletGeoAdmin  # type: ignore
from django.contrib import admin, messages
from django.db.models import Value
from django.db.models.functions import Replace
from django.urls import reverse
from django.utils.html import mark_safe
from member.models import (Actor, Language, Person, Organization, Neighborhood,
                           City, State, Country)
from harvest.models import (Property, Harvest, RequestForParticipation, TreeType,
                            Equipment, EquipmentType, HarvestYield, Comment,
                            PropertyImage, HarvestImage)
from harvest.filters import PropertyOwnerTypeAdminFilter, PropertyHasHarvestAdminFilter
from harvest.forms import (RFPForm, HarvestYieldForm, EquipmentForm, PropertyForm)


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
    # form = HarvestForm
    model = Harvest
    inlines = (PersonInline, HarvestYieldInline, HarvestImageInline)


@admin.register(RequestForParticipation)
class RequestForParticipationAdmin(admin.ModelAdmin):
    form = RFPForm


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    form = EquipmentForm


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3


@admin.register(Property)
class PropertyAdmin(LeafletGeoAdmin):
    model = Property
    inlines = [PropertyImageInline]
    list_display = (
        'short_address',
        'owner_edit',
        'owner_type',
        'owner_phone',
        'owner_email',
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

    @admin.display(description="Harvests")
    def harvests(self, _property):
        return _property.harvests.count()

    @admin.action(description="De-authorized selected properties")
    def reset_authorize(self, request, queryset):
        """Set authorized=None to queryset"""
        queryset.update(**{'authorized': None})
        messages.add_message(request, messages.SUCCESS,
                             "Successfully reset authorizations for this season")

    actions = [reset_authorize]

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
