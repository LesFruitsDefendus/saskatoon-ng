from django.conf.urls import url
from django.urls import include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from . import api

router = routers.DefaultRouter()
router.register('api/harvest', api.HarvestViewset, 'harvest')
router.register('api/property', api.PropertyViewset, 'property')
router.register('api/equipment', api.EquipmentViewset, 'equipment')
# router.register(r'^equipment', views.EquipmentList, 'html_equipment')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

#urlpatterns = router.urls
#urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])