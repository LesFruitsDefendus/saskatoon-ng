from django.urls import path
from . import api

urlpatterns = [
    path('person/create/', api.PersonCreateView.as_view(), name='person-create'),
]
