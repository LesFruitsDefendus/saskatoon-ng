from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from . import api

router = routers.DefaultRouter()
router.register('harvest', api.HarvestViewset, 'harvest')
router.register('harvest/553/', api.HarvestDetailsViewset, 'harvest')
router.register('property', api.PropertyViewset, 'property')
router.register('equipment', api.EquipmentViewset, 'equipment')
router.register('organization', api.OrganizationViewset, 'organization')

urlpatterns = [
    path(r'^index', api.IndexView.as_view()),
]

urlpatterns += router.urls