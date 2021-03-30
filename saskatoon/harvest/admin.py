#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Models registration. 
"""

from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin
from member.models import (Actor, Language, Person, Organization, Neighborhood, City, State, Country)
from harvest.models import (Property, Harvest, RequestForParticipation, TreeType, Equipment, EquipmentType, HarvestYield, Comment, PropertyImage)
from harvest.forms import (RFPForm, HarvestYieldForm, EquipmentForm, PropertyForm)

class PropertyInline(admin.TabularInline):
    model = Property
    extra = 0

class PersonInline(admin.TabularInline):
    model = RequestForParticipation
    verbose_name = "Cueilleurs pour cette récolte"
    verbose_name_plural = "Cueilleurs pour cette récolte"
    form = RFPForm
    exclude = ['creation_date', 'confirmation_date']
    extra = 3


class OrganizationAdmin(admin.ModelAdmin):
    inlines = [
        PropertyInline,
    ]
    search_fields = ['name', 'description']


class HarvestYieldInline(admin.TabularInline):
    model = HarvestYield
    form = HarvestYieldForm


class HarvestAdmin(admin.ModelAdmin):
    # form = HarvestForm
    model = Harvest
    inlines = (PersonInline, HarvestYieldInline)


class RequestForParticipationAdmin(admin.ModelAdmin):
    form = RFPForm


class EquipmentAdmin(admin.ModelAdmin):
    form = EquipmentForm


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3


class PropertyAdmin(LeafletGeoAdmin):
    model = Property
    inlines = [PropertyImageInline]
    form = PropertyForm

admin.site.register(Property, PropertyAdmin)
admin.site.register(Harvest, HarvestAdmin)
admin.site.register(RequestForParticipation, RequestForParticipationAdmin)
admin.site.register(TreeType)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(EquipmentType)
admin.site.register(HarvestYield)
admin.site.register(Comment)
admin.site.register(PropertyImage)
