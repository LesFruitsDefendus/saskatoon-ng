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
    NeighborhoodAutocomplete,
)

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


@pytest.mark.django_db
def test_neighborhood_autocomplete_search(client):
    url = reverse('neighborhood-autocomplete')
    response = client.get(url, {'q': 'Dorval'})

    assert response.status_code == 200

    data = response.json()

    assert 'results' in data

    for item in data['results']:
        assert 'Dorval' in item['text']
