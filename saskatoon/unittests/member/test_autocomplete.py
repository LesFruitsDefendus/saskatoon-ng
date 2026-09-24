import pytest
from django.urls import reverse

from member.autocomplete import (
    PersonAutocomplete,
    ContactAutocomplete,
    AuthUserAutocomplete,
    PickLeaderAutocomplete,
    ActorAutocomplete,
    OwnerAutocomplete,
    EquipmentPointAutocomplete,
)
from member.models import Neighborhood

autocomplete_classes = [
    PersonAutocomplete,
    ContactAutocomplete,
    AuthUserAutocomplete,
    PickLeaderAutocomplete,
    ActorAutocomplete,
    OwnerAutocomplete,
    EquipmentPointAutocomplete,
]


@pytest.mark.parametrize("Autocomplete", autocomplete_classes)
def test_Autocomplete_init(Autocomplete):
    """Test that Autocomplete class can be initialized"""

    autocomplete = Autocomplete()

    assert isinstance(autocomplete, Autocomplete)


@pytest.mark.parametrize("Autocomplete", autocomplete_classes)
def test_Autocomplete_get_queryset_none(Autocomplete):
    """Test that get_queryset method can be called and returns no results"""

    autocomplete = Autocomplete()
    results = autocomplete.get_queryset()

    assert results.count() == 0


@pytest.mark.django_db
def test_neighborhood_autocomplete_search(client):
    neighborhoods = ["Pointe-Saint-Charles", "Saint-Henri", "Verdun"]
    Neighborhood.objects.bulk_create([Neighborhood(name=name) for name in neighborhoods])

    url = reverse('neighborhood-autocomplete')

    for search, expected in [
        (None, neighborhoods),
        ("", neighborhoods),
        ("Pointe", neighborhoods[:1]),
        ("Saint", neighborhoods[:2]),
        ("Mile-End", []),
    ]:
        query = {'q': search} if search is not None else {}
        response = client.get(url, query)
        assert response.status_code == 200
        data = response.json()
        results = [item['text'] for item in data['results']]
        assert results == expected
