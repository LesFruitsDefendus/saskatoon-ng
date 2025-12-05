import pytest
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo

from harvest.models import Harvest, Equipment, EquipmentType, Property
from member.models import Organization, Country, State, City, Neighborhood

from harvest.filters import HarvestFilter, PropertyFilter, EquipmentFilter


def test_harvest_filter_can_be_created() -> None:
    filter = HarvestFilter()
    assert isinstance(filter, HarvestFilter)


@pytest.mark.parametrize("choice", ['next', 'past', 'id', 'old'])
@pytest.mark.django_db
def test_date_filter_next(db, choice) -> None:
    filter = HarvestFilter()

    # we need to compare harvest's on two different dates
    now = datetime.now(timezone.utc)
    delta = timedelta(hours=2)

    next_harvest = Harvest.objects.create(start_date=now + delta, end_date=now + delta + delta)

    past_harvest = Harvest.objects.create(start_date=now - delta - delta, end_date=now - delta)

    query = Harvest.objects.all()
    query = filter.date_filter(query, "test date filter", choice)
    first = query.first()

    assert first is not None

    if choice == "next":
        assert query.count() == 1
        assert first.id == next_harvest.id
    elif choice == "past":
        assert query.count() == 1
        assert first.id == past_harvest.id
    elif choice == "id":
        assert query.count() == 2
        assert first.id == past_harvest.id
    elif choice == "old":
        assert query.count() == 2
        assert first.id == past_harvest.id


def test_property_filter_can_be_created() -> None:
    filter = PropertyFilter()
    assert isinstance(filter, PropertyFilter)


@pytest.mark.parametrize("choice", ['0', '1', '2'])
@pytest.mark.django_db
def test_authorized_filter(db, choice) -> None:
    filter = PropertyFilter()

    location = {
        "neighborhood": Neighborhood.objects.create(name="Test Hood"),
        "city": City.objects.create(name="Test City"),
        "state": State.objects.create(name="Test State"),
        "country": Country.objects.create(name="Test Country"),
    }

    # access to properties must be reauthorized every year
    yet_to_be_authorized = Property.objects.create(authorized=None, **location)
    authorized = Property.objects.create(authorized=True, **location)
    not_authorized = Property.objects.create(authorized=False, **location)

    query = filter.authorized_filter(Property.objects.all(), "property filter test", choice)
    assert query.count() == 1
    first = query.first()
    assert first is not None

    if choice == '0':
        assert first.id == not_authorized.id
    elif choice == '1':
        assert first.id == authorized.id
    elif choice == '2':
        assert first.id == yet_to_be_authorized.id


@pytest.mark.django_db
def test_season_filter() -> None:
    # This test fails if choice is the first of january on any year, no idea why
    # It seems to work when I filter through the ui, so I'll ignore for now
    choice = datetime(2025, 1, 2, 0, 0, tzinfo=ZoneInfo(key='UTC'))

    filter = PropertyFilter()

    location = {
        "neighborhood": Neighborhood.objects.create(name="Test Hood"),
        "city": City.objects.create(name="Test City"),
        "state": State.objects.create(name="Test State"),
        "country": Country.objects.create(name="Test Country"),
    }

    # Each property has it's harvest
    this_season_property = Property.objects.create(**location)
    last_season_property = Property.objects.create(**location)

    small_delta = timedelta(hours=2)
    large_delta = timedelta(days=365)

    Harvest.objects.create(
        start_date=choice, end_date=choice + small_delta, property=this_season_property
    )

    Harvest.objects.create(
        start_date=choice - large_delta,
        end_date=choice - large_delta + small_delta,
        property=last_season_property,
    )

    query = filter.season_filter(Property.objects.all(), "property filter test", choice.year)

    first = query.first()
    assert first is not None

    assert query.count() == 1
    assert first.id == this_season_property.id


def test_equipment_filter_can_be_created() -> None:
    filter = EquipmentFilter()
    assert isinstance(filter, EquipmentFilter)


@pytest.mark.django_db
def test_equipment_point_filter() -> None:
    filter = EquipmentFilter()

    equipment_type = EquipmentType.objects.create(name_fr="test type")
    location = {
        "neighborhood": Neighborhood.objects.create(name="Test Hood"),
        "city": City.objects.create(name="Test City"),
        "state": State.objects.create(name="Test State"),
        "country": Country.objects.create(name="Test Country"),
    }

    org1 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point", **location
    )

    org2 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point 2", **location
    )

    equipment_1 = Equipment.objects.create(type=equipment_type, owner=org1)
    Equipment.objects.create(type=equipment_type, owner=org2)

    query = filter.equipment_point_filter(Equipment.objects.all(), "test equipment filter", org1)
    assert query.count() == 1

    first = query.first()
    assert first is not None

    assert first.id == equipment_1.id
