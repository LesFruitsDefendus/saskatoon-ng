from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.auth.views import LoginView, LogoutView
from . import api

router = routers.DefaultRouter()
router.register('harvest', api.HarvestViewset, 'harvest')
router.register('property', api.PropertyViewset, 'property')
router.register('equipment', api.EquipmentViewset, 'equipment')

urlpatterns = [
    url(r'^index', api.IndexView.as_view()),
    url(r'^', include(router.urls)),
    url(r'^logout/', LogoutView.as_view(), name="logout"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

