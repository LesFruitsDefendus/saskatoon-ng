import pytest
import deal
from datetime import timedelta, datetime, timezone
import hypothesis.strategies as st

from django.conf import settings
from sitebase.utils import parse_naive_datetime
from member.utils import get_available_equipment_points
from harvest.models import Harvest, Equipment, EquipmentType
from member.models import Organization, Country, State, City, Neighborhood

tzinfo = timezone(timedelta(hours=-5))
start = datetime(2025, 3, 2, hour=12, minute=0, second=0, microsecond=0, tzinfo=tzinfo)
end = datetime(2025, 3, 2, hour=18, minute=0, second=0, microsecond=0, tzinfo=tzinfo)


@pytest.fixture
def harvest(db, request) -> Harvest:
    return Harvest.objects.create(status=request.param, start_date=start, end_date=end)


@pytest.fixture
def second_harvest(db, request) -> Harvest:
    return Harvest.objects.create(status=request.param, start_date=start, end_date=end)


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


"""
@pytest.mark.django_db
def test_available_equipment_points_fuzz() -> None:
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
"""

# For all cases, we assume that harvests can only reserve an equipment point
# if they are scheduled or ready and that all equipment point reservations for
# successfull harvests are in the past.


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_end_during(db, harvest, equipment) -> None:
    """
    If the requested end time is during another reservation,
    there should be no available equipment points.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        start.replace(hour=7),
        end.replace(hour=14),
        None,
    )

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_start_during(db, harvest, equipment) -> None:
    """
    If the requested start time is during another reservation,
    there should no available equipment points.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        start.replace(hour=14),
        end.replace(hour=20),
        None,
    )

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_around(db, harvest, equipment) -> None:
    """
    If both the requested start and end time is during
    another reservation, there should be no available equipment
    points.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        start.replace(hour=14),
        end.replace(hour=16),
        None,
    )

    print(harvest.start_date)
    print(harvest.start_date + timedelta(hours=2))

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_same_dates(db, harvest, equipment) -> None:
    """
    If the requested times are at the same time as another reservation,
    there should be no available equipment points.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(harvest.start_date, harvest.end_date)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_no_conflict_with_self(db, harvest, equipment) -> None:
    """
    If the harvest has already reserved an equipment point, that equipment point should still
    be listed as available for itself.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(harvest.start_date, harvest.end_date, harvest)

    assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", [Harvest.Status.SCHEDULED], indirect=True)
@pytest.mark.parametrize("second_harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_conflict_when_checking_self(
    db, harvest, second_harvest, equipment
) -> None:
    """
    If harvest one has already reserved an equipment point and we check if
    a harvest two is conflicting with itself, that equipment point should
    be unavailable.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        second_harvest.start_date, second_harvest.end_date, second_harvest
    )

    assert points.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_after(db, harvest, equipment) -> None:
    """
    There should be an available equipment point if all
    other reservations are in the past.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        start.replace(hour=20),
        end.replace(hour=22),
        None,
    )

    assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_before(db, harvest, equipment) -> None:
    """
    There should be an available equipment point if the next
    reservation if further then the alloted buffer
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        start.replace(hour=8),
        end.replace(hour=10),
        None,
    )

    assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_buffer_after(db, harvest, equipment) -> None:
    """
    There should be no available equipment points right after a reservation.
    """

    harvest.equipment_reserved.set([equipment])
    points = get_available_equipment_points(
        start.replace(hour=18),
        end.replace(hour=20),
        None,
    )

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_buffer_before(db, harvest, equipment) -> None:
    """
    There should be no available equipment points right before a reservation
    """

    harvest.equipment_reserved.set([equipment])

    points = get_available_equipment_points(
        start.replace(hour=8),
        end.replace(hour=12),
        None,
    )

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_buffer_with_parse_naive_datetime(
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

    points = get_available_equipment_points(end.replace(hour=13), end.replace(hour=14), None)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
@pytest.mark.parametrize("second_harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_date_change_after_reservation(
    db, harvest, second_harvest, equipment
) -> None:
    """
    If two harvests reserve an equipment point at different times,
    the second one should not be able to change it's time
    to the first one without abandonning it's reservation.
    """

    harvest.equipment_reserved.set([equipment])
    second_harvest.start_date = start.replace(day=1)
    second_harvest.end_date = end.replace(day=1)

    before_change_points = get_available_equipment_points(
        start,
        end,
        second_harvest,
    )

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert before_change_points.count() == 0
    else:
        assert before_change_points.count() == 1

    second_harvest.equipment_reserved.set([equipment])

    second_harvest.start_date = start.replace(day=2)
    second_harvest.end_date = end.replace(day=2)

    after_change_points = get_available_equipment_points(
        start,
        end,
        second_harvest,
    )

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert after_change_points.count() == 0
    else:
        assert after_change_points.count() == 1
