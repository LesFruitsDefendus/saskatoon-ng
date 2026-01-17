import pytest
from typing import TypedDict

from member.models import Country, State, City, Neighborhood


Location = TypedDict(
    'Location',
    {
        'neighborhood': Neighborhood,
        'city': City,
        'state': State,
        'country': Country,
    },
)


@pytest.fixture
def location(db) -> Location:
    return {
        'neighborhood': Neighborhood.objects.create(name="Test Hood"),
        'city': City.objects.create(name="Test City"),
        'state': State.objects.create(name="Test State"),
        'country': Country.objects.create(name="Test Country"),
    }
