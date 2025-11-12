import pytest

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
    NeighborhoodAutocomplete,
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
