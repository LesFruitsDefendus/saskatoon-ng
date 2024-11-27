from django.urls import path, re_path
from . import views, autocomplete
from harvest import api

urlpatterns = [

    # LIST VIEWS
    path('beneficiaries/',
         api.BeneficiaryListView.as_view(),
         name='beneficiary-list'),

    path('equipment-points/',
         api.EquipmentPointListView.as_view(),
         name='equipment-point-list'),


    # RETRIEVE VIEWS
    path('organization/<int:pk>',
         api.OrganizationRetrieveView.as_view(),
         name='organization-detail'),


    # CREATE VIEWS
    path('person/create/',
         views.PersonCreateView.as_view(),
         name='person-create'),

    path('organization/create/',
         views.OrganizationCreateView.as_view(),
         name='organization-create'),

    # UPDATE VIEWS
    path('person/update/<int:pk>/',
         views.PersonUpdateView.as_view(),
         name='person-update'),

    path('person/onboarding_update/<int:pk>/',
         views.OnboardingPersonUpdateView.as_view(),
         name='onboarding-person-update'),

    path('organization/update/<int:pk>/',
         views.OrganizationUpdateView.as_view(),
         name='organization-update'),

    path('user/change_password/',
         views.PasswordChangeView.as_view(),
         name='change-password'),

    path('user/reset_password/<int:pk>',
         views.PasswordResetView.as_view(),
         name='reset-password'),

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

    re_path(r'^owner-autocomplete/$',
            autocomplete.OwnerAutocomplete.as_view(),
            name='owner-autocomplete'),

    re_path(r'^equipmentpoint-autocomplete/$',
            autocomplete.EquipmentPointAutocomplete.as_view(),
            name='equipmentpoint-autocomplete'),

    re_path(r'^contact-autocomplete/$',
            autocomplete.ContactAutocomplete.as_view(),
            name='contact-autocomplete'),
]
