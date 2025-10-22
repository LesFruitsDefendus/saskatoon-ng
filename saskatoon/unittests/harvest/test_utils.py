import pytest
import deal
from datetime import timedelta, datetime, timezone
import hypothesis.strategies as st

from harvest.utils import available_equipment_points
from harvest.models import Harvest, Equipment, EquipmentType
from member.models import Organization, Country, State, City, Neighborhood


@pytest.fixture
def harvest(db) -> Harvest:
    hood = Neighborhood.objects.create(name="Test Hood")
    city = City.objects.create(name="Test City")
    state = State.objects.create(name="Test State")
    country = Country.objects.create(name="Test Country")
    org = Organization.objects.create(
        is_equipment_point=True,
        civil_name="Test Equipment Point",
        neighborhood=hood,
        city=city,
        state=state,
        country=country,
    )
    equip_type = EquipmentType.objects.create(name_fr="Type d'Equipement Test")
    equip = Equipment.objects.create(
        type=equip_type,
        owner=org,
        shared=True,
    )

    tzinfo = timezone(timedelta(hours=-5))
    now = datetime.now(tzinfo)
    delta = delta = timedelta(hours=2)

    harvest = Harvest.objects.create(
        status=Harvest.Status.SCHEDULED,
        start_date=now,
        end_date=now + delta
    )
    harvest.equipment_reserved.set([equip])

    harvest = Harvest.objects.create(
        status=Harvest.Status.CANCELLED,
        start_date=now,
        end_date=now + delta
    )
    harvest.equipment_reserved.set([equip])

    return harvest


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
        kwargs=dict(
            start=date_strat,
            end=date_strat
        ),
    )

    for case in cases:
        case()


@pytest.mark.django_db
def test_available_equipment_points_end_during(db, harvest) -> None:
    """Check availability when it ends during another harvest"""

    points = available_equipment_points(
        harvest.start_date - timedelta(hours=5),
        harvest.end_date - timedelta(hours=1),
        timedelta(hours=1)
    )

    assert points.count() == 0


@pytest.mark.django_db
def test_available_equipment_points_start_during(db, harvest) -> None:
    """Check availability when it starts during another harvest"""

    points = available_equipment_points(
        harvest.start_date + timedelta(hours=1),
        harvest.end_date + timedelta(hours=5),
        timedelta(hours=1)
    )

    assert points.count() == 0


@pytest.mark.django_db
def test_available_equipment_points_same_dates(db, harvest) -> None:
    """Check availability on the same time as another harvest"""

    points = available_equipment_points(harvest.start_date, harvest.end_date, timedelta(hours=1))
    assert points.count() == 0


@pytest.mark.django_db
def test_available_equipment_points_after(db, harvest) -> None:
    """Check availability after another harvest"""

    delta = timedelta(hours=4)
    points = available_equipment_points(
        harvest.start_date + delta,
        harvest.end_date + delta,
        timedelta(hours=1)
    )

    assert points.count() == 1


@pytest.mark.django_db
def test_available_equipment_points_before(db, harvest) -> None:
    """Check availability before another harvest"""

    delta = timedelta(hours=4)
    points = available_equipment_points(
        harvest.start_date - delta,
        harvest.end_date - delta,
        timedelta(hours=1)
    )

    assert points.count() == 1


@pytest.mark.django_db
def test_available_equipment_points_buffer(db, harvest) -> None:
    """Check availability right after another harvest"""

    delta = timedelta(hours=2)
    points = available_equipment_points(
        harvest.start_date + delta,
        harvest.end_date + delta,
        timedelta(hours=1)
    )

    assert points.count() == 0
