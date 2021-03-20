#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Models registration. 
"""

# from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin
from member.models import (Actor, Language, Person, Organization, Neighborhood, City, State, Country)
from harvest.models import (Property, Harvest, RequestForParticipation, TreeType, Equipment, EquipmentType, HarvestYield, Comment)

admin.site.register(Property)
admin.site.register(Harvest)
admin.site.register(RequestForParticipation)
admin.site.register(TreeType)
admin.site.register(Equipment)
admin.site.register(EquipmentType)
admin.site.register(HarvestYield)
admin.site.register(Comment)

admin.site.register(Actor)
admin.site.register(Language)
admin.site.register(Person)
admin.site.register(Organization)
admin.site.register(Neighborhood)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)
