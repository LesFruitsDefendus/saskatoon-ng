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


@pytest.mark.django_db
def test_neighborhood_autocomplete_search(client):
    Neighborhood.objects.create(name="Verdun")
    Neighborhood.objects.create(name="Plateau-Mont-Royal")

    url = reverse('neighborhood-autocomplete')
    response = client.get(url, {'q': 'Plat'})

    assert response.status_code == 200
    data = response.json()
    assert 'results' in data

    results = data['results']
    assert len(results) == 1

    returned_texts = [item['text'] for item in results]

    for text in returned_texts:
        assert 'Plateau-Mont-Royal' in text

    response = client.get(url, {'q': ''})
    data = response.json()
    results = data['results']

    assert len(results) == 2

    response = client.get(url, {'q': 'Mile End'})
    data = response.json()
    results = data['results']

    assert len(results) == 0
