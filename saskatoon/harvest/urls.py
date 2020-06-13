from rest_framework import routers
from .api import HarvestViewset, PropertyViewset

router = routers.DefaultRouter()
router.register('api/harvest', HarvestViewset, 'harvest')
router.register('api/property', PropertyViewset, 'property')

urlpatterns = router.urls
