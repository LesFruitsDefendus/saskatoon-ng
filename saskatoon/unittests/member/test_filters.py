import pytest
from datetime import datetime, timezone

from harvest.models import Harvest, Equipment, EquipmentType
from member.models import Organization
from member.filters import CommunityFilter, OrganizationFilter, EquipmentPointFilter

# ruff tries to erase it because the weird way pytest applies
# fixtures is not recognised.
from unittests.member.fixtures import location  # noqa: F401


def test_community_filter_can_be_created() -> None:
    filter = CommunityFilter()
    assert isinstance(filter, CommunityFilter)


# TODO: Add community filter tests


def test_organization_filter_can_be_created() -> None:
    filter = OrganizationFilter()
    assert isinstance(filter, OrganizationFilter)


# TODO: Add organization filter tests


def test_equipment_point_filter_can_be_created() -> None:
    filter = EquipmentPointFilter()
    assert isinstance(filter, EquipmentPointFilter)


@pytest.mark.django_db
def test_beneficiary_filter(location) -> None:  # noqa: F811
    filter = EquipmentPointFilter()

    org1 = Organization.objects.create(
        is_beneficiary=True, civil_name=" Test Beneficiary", **location
    )

    Organization.objects.create(is_beneficiary=False, civil_name=" Test Organization", **location)

    query = filter.beneficiary_filter(Organization.objects.all(), "test beneficiary filter", True)
    assert query.count() == 1

    first = query.first()
    assert first is not None
    assert first.actor_id == org1.actor_id


@pytest.mark.django_db
def test_equipment_type_filter(location) -> None:  # noqa: F811
    filter = EquipmentPointFilter()

    equipment_type = EquipmentType.objects.create(name_fr="test type")
    equipment_type2 = EquipmentType.objects.create(name_fr="test type 2")

    org1 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point", **location
    )

    org2 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point 2", **location
    )

    Equipment.objects.create(type=equipment_type, owner=org1)
    Equipment.objects.create(type=equipment_type2, owner=org2)

    query = filter.equipment_type_filter(
        Organization.objects.all(), "test equipment type filter", equipment_type
    )
    assert query.count() == 1

    first = query.first()
    assert first is not None
    assert first.actor_id == org1.actor_id


@pytest.mark.django_db
def test_start_date_filter() -> None:
    filter = EquipmentPointFilter()
    date = datetime.now(timezone.utc)
    query = filter.start_date_filter(Organization.objects.all(), "test start date filter", date)

    assert filter.start_val == date
    assert query.count() == Organization.objects.all().count()


@pytest.mark.django_db
def test_end_date_filter() -> None:
    filter = EquipmentPointFilter()
    date = datetime.now(timezone.utc)
    query = filter.end_date_filter(Organization.objects.all(), "test end date filter", date)

    assert filter.end_val == date
    assert query.count() == Organization.objects.all().count()


@pytest.mark.django_db
def test_status_filter() -> None:
    filter = EquipmentPointFilter()
    query = filter.status_filter(Organization.objects.all(), "test status filter", '1')

    assert filter.status_val == '1'
    assert query.count() == Organization.objects.all().count()


@pytest.mark.django_db
def test_filter_queryset_reserved(location) -> None:  # noqa: F811
    filter = EquipmentPointFilter()
    filter.status_val = '1'

    equipment_type = EquipmentType.objects.create(name_fr="test type")
    equipment_type2 = EquipmentType.objects.create(name_fr="test type 2")

    org1 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point", **location
    )

    org2 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point 2", **location
    )

    equipment_1 = Equipment.objects.create(type=equipment_type, owner=org1)
    Equipment.objects.create(type=equipment_type2, owner=org2)

    harvest = Harvest.objects.create(
        start_date=filter.start_val, end_date=filter.end_val, status=Harvest.Status.SCHEDULED
    )
    harvest.equipment_reserved.set([equipment_1])
    query = filter.filter_queryset(Organization.objects.all())
    assert query.count() == 1

    first = query.first()
    assert first is not None
    assert first.actor_id == org1.actor_id


@pytest.mark.django_db
def test_filter_queryset_available(location) -> None:  # noqa: F811
    filter = EquipmentPointFilter()
    filter.status_val = '2'

    equipment_type = EquipmentType.objects.create(name_fr="test type")
    equipment_type2 = EquipmentType.objects.create(name_fr="test type 2")

    org1 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point", **location
    )

    org2 = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point 2", **location
    )

    equipment_1 = Equipment.objects.create(type=equipment_type, owner=org1)
    Equipment.objects.create(type=equipment_type2, owner=org2)

    harvest = Harvest.objects.create(
        start_date=filter.start_val, end_date=filter.end_val, status=Harvest.Status.SCHEDULED
    )
    harvest.equipment_reserved.set([equipment_1])

    query = filter.filter_queryset(Organization.objects.all())
    assert query.count() == 1

    first = query.first()
    assert first is not None
    assert first.actor_id == org2.actor_id
