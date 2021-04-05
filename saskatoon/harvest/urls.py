from django.urls import include, path, re_path
from rest_framework import routers
from . import api

router = routers.DefaultRouter()
router.register('harvest', api.HarvestViewset, 'harvest')
router.register('property', api.PropertyViewset, 'property')
router.register('equipment', api.EquipmentViewset, 'equipment')
router.register('beneficiary', api.BeneficiaryViewset, 'organization')
router.register('community', api.CommunityViewset, 'community')
router.register('participation', api.RequestForParticipationViewset, 'participation')

urlpatterns = [
    path(r'', api.IndexView.as_view()),
    path(r'equipment/create', api.EquipmentCreateView.as_view()),
    path(r'property/create', api.PropertyCreateView.as_view()),
    path(r'property/create_public', api.PropertyCreatePublicView.as_view()),
    path(r'harvest/create', api.HarvestCreateView.as_view()),
    path(r'participation/create', api.RequestForParticipationCreateView.as_view()),
    re_path(r'^actor-autocomplete/$', api.ActorAutocomplete.as_view(), name='actor-autocomplete'),
    re_path(r'^property-autocomplete/$', api.PropertyAutocomplete.as_view(), name='property-autocomplete'),
    re_path(r'^tree-autocomplete/$', api.TreeAutocomplete.as_view(), name='tree-autocomplete'),
    re_path(r'^pickleader-autocomplete/$', api.PickLeaderAutocomplete.as_view(), name='pickleader-autocomplete'),
]

urlpatterns += router.urls