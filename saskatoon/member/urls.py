from django.urls import path
from . import api

urlpatterns = [

    path('person/create/',
         api.PersonCreateView.as_view(),
         name='person-create'),

    path('person/update/<int:pk>/',
         api.PersonUpdateView.as_view(),
         name='person-update'),

    path('organization/create/',
         api.OrganizationCreateView.as_view(),
         name='organization-create'),

    path('organization/update/<int:pk>/',
         api.OrganizationUpdateView.as_view(),
         name='organization-update'),
]
