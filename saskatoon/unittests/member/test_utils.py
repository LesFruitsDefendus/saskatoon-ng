import pytest
import deal
from datetime import timedelta, datetime, timezone
import hypothesis.strategies as st

from django.conf import settings
from sitebase.utils import parse_naive_datetime
from member.utils import is_equipment_point_available, get_available_equipment_points
from harvest.models import Harvest, Equipment, EquipmentType
from member.models import Organization, Country, State, City, Neighborhood

TZINFO = timezone(timedelta(hours=-5))
HARVEST_START = datetime(2025, 3, 2, hour=12, tzinfo=TZINFO)
HARVEST_END = datetime(2025, 3, 2, hour=18, tzinfo=TZINFO)


@pytest.fixture
def harvest(db, request) -> Harvest:
    return Harvest.objects.create(
        status=request.param, start_date=HARVEST_START, end_date=HARVEST_END
    )


@pytest.fixture
def second_harvest(db, request) -> Harvest:
    return Harvest.objects.create(
        status=request.param, start_date=HARVEST_START, end_date=HARVEST_END
    )


@pytest.fixture
def equipment(db) -> Equipment:
    """Creates an organization with two equipments, then return one."""
    location = {
        "neighborhood": Neighborhood.objects.create(name="Test Hood"),
        "city": City.objects.create(name="Test City"),
        "state": State.objects.create(name="Test State"),
        "country": Country.objects.create(name="Test Country"),
    }

    org = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point", **location
    )

    equip_type = EquipmentType.objects.create(name_fr="Type d'Equipement Test")

    equipment = Equipment.objects.create(
        type=equip_type,
        owner=org,
        shared=True,
    )
    # A second equipment that is not reserved allows us to test that renting any part
    # of an equipment point makes the entire equipment point unavailable.
    Equipment.objects.create(
        type=equip_type,
        owner=org,
        shared=True,
    )

    return equipment


@pytest.mark.django_db
def test_get_available_equipment_points_fuzz() -> None:
    start_strat = st.datetimes(
        min_value=datetime.min,
        max_value=datetime.max - timedelta(hours=1),
        timezones=st.timezones(),
        allow_imaginary=True,
    )

    end_strat = start_strat.flatmap(
        lambda d: st.datetimes(
            timezones=st.just(d.tzinfo),
            min_value=d.replace(tzinfo=None),
            max_value=datetime.max,
            allow_imaginary=True,
        ),
    )

    cases = deal.cases(
        func=get_available_equipment_points,
        kwargs=dict(start=start_strat, end=end_strat, harvest=st.just(None)),
    )

    for case in cases:
        case()


# For all cases, we assume that harvests can only reserve an equipment point
# if they are scheduled or ready and that all equipment point reservations for
# successfull harvests are in the past.


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_end_during(db, harvest, equipment) -> None:
    """
    If the requested end time is during another reservation,
    there should be no available equipment points.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=7),
        HARVEST_END.replace(hour=14),
        None,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_start_during(db, harvest, equipment) -> None:
    """
    If the requested start time is during another reservation,
    there should no available equipment points.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=14),
        HARVEST_END.replace(hour=20),
        None,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_around(db, harvest, equipment) -> None:
    """
    If both the requested start and end time is during
    another reservation, there should be no available equipment
    points.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=14),
        HARVEST_END.replace(hour=16),
        None,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_same_dates(db, harvest, equipment) -> None:
    """
    If the requested times are at the same time as another reservation,
    there should be no available equipment points.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(equipment.owner, harvest.start_date, harvest.end_date)

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_no_conflict_with_self(db, harvest, equipment) -> None:
    """
    If the harvest has already reserved an equipment point, that equipment point should still
    be listed as available for itself.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner, harvest.start_date, harvest.end_date, harvest
    )

    assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", [Harvest.Status.SCHEDULED], indirect=True)
@pytest.mark.parametrize("second_harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_conflict_when_checking_self(
    db, harvest, second_harvest, equipment
) -> None:
    """
    If harvest one has already reserved an equipment point and we check if
    a harvest two is conflicting with itself, that equipment point should
    be unavailable.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner, second_harvest.start_date, second_harvest.end_date, second_harvest
    )

    assert available is False


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_after(db, harvest, equipment) -> None:
    """
    There should be an available equipment point if all
    other reservations are in the past.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=20),
        HARVEST_END.replace(hour=22),
        None,
    )

    assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_before(db, harvest, equipment) -> None:
    """
    There should be an available equipment point if the next
    reservation if further then the alloted buffer
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=8),
        HARVEST_END.replace(hour=10),
        None,
    )

    assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_buffer_after(db, harvest, equipment) -> None:
    """
    There should be no available equipment points right after a reservation.
    """

    harvest.equipment_reserved.set([equipment])
    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=18),
        HARVEST_END.replace(hour=20),
        None,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_buffer_before(db, harvest, equipment) -> None:
    """
    There should be no available equipment points right before a reservation
    """

    harvest.equipment_reserved.set([equipment])

    available = is_equipment_point_available(
        equipment.owner,
        HARVEST_START.replace(hour=8),
        HARVEST_END.replace(hour=12),
        None,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_buffer_with_parse_naive_datetime(
    db, harvest, equipment
) -> None:
    """
    Regression test for when dates are passed through the autocompletete,
    we where getting dates with a -5:18 timezone instead of -5
    """

    harvest.equipment_reserved.set([equipment])

    end_str = harvest.end_date.replace(tzinfo=None).strftime(settings.DATETIME_INPUT_FORMATS[0])
    end = parse_naive_datetime(end_str, settings.DATETIME_INPUT_FORMATS[0])
    assert end is not None

    available = is_equipment_point_available(
        equipment.owner, HARVEST_END.replace(hour=13), HARVEST_END.replace(hour=14), None
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available is False
    else:
        assert available is True


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
@pytest.mark.parametrize("second_harvest", Harvest.Status, indirect=True)
def test_is_equipment_point_available_date_change_after_reservation(
    db, harvest, second_harvest, equipment
) -> None:
    """
    If two harvests reserve an equipment point at different times,
    the second one should not be able to change it's time
    to the first one without abandoning it's reservation.
    """

    harvest.equipment_reserved.set([equipment])
    second_harvest.start_date = HARVEST_START.replace(day=1)
    second_harvest.end_date = HARVEST_END.replace(day=1)

    available_before_change = is_equipment_point_available(
        equipment.owner,
        HARVEST_START,
        HARVEST_END,
        second_harvest,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available_before_change is False
    else:
        assert available_before_change is True

    second_harvest.equipment_reserved.set([equipment])

    second_harvest.start_date = HARVEST_START.replace(day=2)
    second_harvest.end_date = HARVEST_END.replace(day=2)

    available_after_change = is_equipment_point_available(
        equipment.owner,
        HARVEST_START,
        HARVEST_END,
        second_harvest,
    )

    if harvest.status in Harvest.CAN_RESERVE_EQUIPMENT:
        assert available_after_change is False
    else:
        assert available_after_change is True
