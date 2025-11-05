import pytest
import deal
from datetime import timedelta, datetime, timezone
import hypothesis.strategies as st

from member.utils import available_equipment_points
from harvest.models import Harvest, Equipment, EquipmentType
from member.models import Organization, Country, State, City, Neighborhood


@pytest.fixture
def harvest(db, request) -> Harvest:
    tzinfo = timezone(timedelta(hours=-5))
    now = datetime.now(tzinfo)
    delta = delta = timedelta(hours=2)

    return Harvest.objects.create(status=request.param,
                                  start_date=now,
                                  end_date=now + delta)


@pytest.fixture
def second_harvest(db, request) -> Harvest:
    tzinfo = timezone(timedelta(hours=-5))
    now = datetime.now(tzinfo)
    delta = delta = timedelta(hours=2)

    return Harvest.objects.create(status=request.param,
                                  start_date=now,
                                  end_date=now + delta)


@pytest.fixture
def equipment(db) -> Equipment:
    location = {
        'neighborhood': Neighborhood.objects.create(name="Test Hood"),
        'city': City.objects.create(name="Test City"),
        'state': State.objects.create(name="Test State"),
        'country': Country.objects.create(name="Test Country")
    }

    org = Organization.objects.create(is_equipment_point=True,
                                      civil_name=" Test Equipment Point",
                                      **location)

    equip_type = EquipmentType.objects.create(name_fr="Type d'Equipement Test")

    equipment = Equipment.objects.create(
        type=equip_type,
        owner=org,
        shared=True,
    )
    """ A second equipment that is not reserved allows us to test that renting any part
          of an equipment point makes the entire equipment point unavailable. """
    Equipment.objects.create(
        type=equip_type,
        owner=org,
        shared=True,
    )

    return equipment


@pytest.mark.django_db
def test_available_equipment_points_fuzz() -> None:
    date_strat = st.datetimes(
        min_value=datetime.min,
        max_value=datetime.max,
        timezones=st.timezones(),
        allow_imaginary=True,
    )

    cases = deal.cases(
        func=available_equipment_points,
        kwargs=dict(start=date_strat, end=date_strat),
    )

    for case in cases:
        case()


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_end_during(db, harvest, equipment) -> None:
    """
        If the requested end time conflicts with another harvest,
        there should only be an available equipment point if conflicting
        harvests are not scheduled or ready
    """

    harvest.equipment_reserved.set([equipment])
    points = available_equipment_points(
        harvest.start_date - timedelta(hours=5),
        harvest.end_date - timedelta(hours=1), None)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_start_during(db, harvest,
                                                 equipment) -> None:
    """
        If the requested start time conflicts with another harvest,
        there should only be an available equipment point if conflicting
        harvests are not scheduled or ready
    """

    harvest.equipment_reserved.set([equipment])
    points = available_equipment_points(
        harvest.start_date + timedelta(hours=1),
        harvest.end_date + timedelta(hours=5), None)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_same_dates(db, harvest, equipment) -> None:
    """
        There should only be an available equipment point if concurrent harvests
        are not scheduled or ready
    """

    harvest.equipment_reserved.set([equipment])
    points = available_equipment_points(harvest.start_date, harvest.end_date,
                                        None)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_no_conflict_with_self(
        db, harvest, equipment) -> None:
    """
        If the harvest has already reserved an equipment point, that equipment point should still
        be listed as available for itself.
    """

    harvest.equipment_reserved.set([equipment])
    points = available_equipment_points(harvest.start_date, harvest.end_date,
                                        harvest)

    assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", [Harvest.Status.SCHEDULED], indirect=True)
@pytest.mark.parametrize("second_harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_conflict_when_checking_self(
        db, harvest, second_harvest, equipment) -> None:
    """
        If a harvest has already reserved an equipment point and we check if
        a second harvest is conflicting with itself, that equipment point should
        be unavailable be listed as available for itself.
    """

    harvest.equipment_reserved.set([equipment])
    points = available_equipment_points(second_harvest.start_date,
                                        second_harvest.end_date,
                                        second_harvest)

    assert points.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_after(db, harvest, equipment) -> None:
    """
        There should be an available equipment point if all
        other harvests have passed
    """

    harvest.equipment_reserved.set([equipment])
    delta = timedelta(hours=4)
    points = available_equipment_points(harvest.start_date + delta,
                                        harvest.end_date + delta, None)

    assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_before(db, harvest, equipment) -> None:
    """
        There should be an available equipment point if the next
        harvest if further then the alloted buffer
    """

    harvest.equipment_reserved.set([equipment])
    delta = timedelta(hours=4)
    points = available_equipment_points(harvest.start_date - delta,
                                        harvest.end_date - delta, None)

    assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_buffer_after(db, harvest,
                                                 equipment) -> None:
    """
        There should be no available equipment points right after
        a scheduled or ready harvest
    """

    harvest.equipment_reserved.set([equipment])
    delta = timedelta(hours=2)
    points = available_equipment_points(harvest.start_date + delta,
                                        harvest.end_date + delta, None)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("harvest", Harvest.Status, indirect=True)
def test_available_equipment_points_buffer_before(db, harvest,
                                                  equipment) -> None:
    """
        There should be no available equipment points right before
        a scheduled or ready harvest
    """

    harvest.equipment_reserved.set([equipment])
    delta = timedelta(hours=2)
    points = available_equipment_points(harvest.start_date + delta,
                                        harvest.end_date + delta, None)

    if harvest.status in [Harvest.Status.SCHEDULED, Harvest.Status.READY]:
        assert points.count() == 0
    else:
        assert points.count() == 1
