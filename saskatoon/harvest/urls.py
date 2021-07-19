from django.urls import include, path, re_path
from rest_framework import routers
from django.views.generic import TemplateView
from . import api

router = routers.DefaultRouter()
router.register('harvest', api.HarvestViewset, 'harvest')
router.register('property', api.PropertyViewset, 'property')
router.register('equipment', api.EquipmentViewset, 'equipment')
router.register('beneficiary', api.BeneficiaryViewset, 'organization')
router.register('community', api.CommunityViewset, 'community')
router.register('participation', api.RequestForParticipationViewset, 'participation')

urlpatterns = [
    # CREATE VIEWS
    path(r'equipment/create', api.EquipmentCreateView.as_view()),
    path(r'property/create', api.PropertyCreateView.as_view()),
    path(r'property/create_public', api.PropertyCreatePublicView.as_view()),
    path(r'harvest/create', api.HarvestCreateView.as_view()),
    path(r'participation/create', api.RequestForParticipationCreateView.as_view()),
    path(r'comment/create', api.CommentCreateView.as_view()),

    # UPDATE VIEWS
    re_path(r'^property/update/(?P<pk>\d+)/$', api.PropertyUpdateView.as_view(), name='property-update'),
    re_path(r'^participation/update/(?P<pk>\d+)/$', api.RequestForParticipationUpdateView.as_view(), name='participation-update'),
    re_path(r'^harvest/update/(?P<pk>\d+)/$', api.HarvestUpdateView.as_view(), name='harvest-update'),
    re_path(r'^equipment/update/(?P<pk>\d+)/$', api.EquipmentUpdateView.as_view(), name='equipment-update'),

    # Fruit Distributions
    path('yield/create/', api.harvest_yield_create, name='harvest-yield-create'),
    path('yield/delete/<int:id>', api.harvest_yield_delete, name='harvest-yield-delete'),

    # AUTO-COMPLET VIEWS
    re_path(r'^actor-autocomplete/$', api.ActorAutocomplete.as_view(), name='actor-autocomplete'),
    re_path(r'^property-autocomplete/$', api.PropertyAutocomplete.as_view(), name='property-autocomplete'),
    re_path(r'^tree-autocomplete/$', api.TreeAutocomplete.as_view(), name='tree-autocomplete'),
    re_path(r'^pickleader-autocomplete/$', api.PickLeaderAutocomplete.as_view(), name='pickleader-autocomplete'),

    # MISC
    path(r'property/thanks', api.TemplateView.as_view(template_name='app/property_thanks.html')),
    path(r'stats', api.TemplateView.as_view(template_name='app/stats.html'), name='statistics'),

]

urlpatterns += router.urls
