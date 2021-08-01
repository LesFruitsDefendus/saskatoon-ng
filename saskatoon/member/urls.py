from django.urls import path, re_path
from . import api, autocomplete

urlpatterns = [

    # CREATE VIEWS
    path('person/create/',
         api.PersonCreateView.as_view(),
         name='person-create'),

    path('organization/create/',
         api.OrganizationCreateView.as_view(),
         name='organization-create'),

    # UPDATE VIEWS
    path('person/update/<int:pk>/',
         api.PersonUpdateView.as_view(),
         name='person-update'),

    path('organization/update/<int:pk>/',
         api.OrganizationUpdateView.as_view(),
         name='organization-update'),


    # AUTO-COMPLETE VIEWS
    re_path(r'^actor-autocomplete/$',
            autocomplete.ActorAutocomplete.as_view(),
            name='actor-autocomplete'),

    re_path(r'^person-autocomplete/$',
            autocomplete.PersonAutocomplete.as_view(),
            name='person-autocomplete'),

    re_path(r'^pickleader-autocomplete/$',
            autocomplete.PickLeaderAutocomplete.as_view(),
            name='pickleader-autocomplete'),
]
