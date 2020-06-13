from rest_framework import routers
from .api import HarvestViewset

router = routers.DefaultRouter()
router.register('api/harvest', HarvestViewset, 'harvest')

urlpatterns = router.urls
