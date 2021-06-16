from django.urls import path
from . import api

urlpatterns = [
    path('person/create/', api.PersonCreateView.as_view(), name='person-create'),
    path('person/update/<int:pk>', api.PersonUpdateView.as_view(), name='person-update'),
]
