"""
Statuses in Harvest.CAN_HAVE_RESERVATION_STATUSES can keep an equipment reservation,
but only those in Harvest.CAN_MAKE_RESERVATION_STATUSES can make a new one.
"""

import re
from datetime import datetime, timedelta, timezone

import pytest
from django import forms
from django.urls import reverse

from harvest.forms import HarvestForm
from harvest.models import Equipment, EquipmentType, Harvest
from member.models import Organization
from unittests.member.fixtures import Location, location  # noqa: F401


@pytest.fixture
def harvest(db) -> Harvest:
    start = datetime(2026, 7, 1, hour=12, tzinfo=timezone.utc)
    end = start + timedelta(hours=4)
    return Harvest.objects.create(start_date=start, end_date=end)


@pytest.fixture
def equipment_point(location: Location) -> Organization:  # noqa: F811
    org = Organization.objects.create(is_equipment_point=True, civil_name="Point", **location)
    Equipment.objects.create(
        type=EquipmentType.objects.create(name_fr="Type"), owner=org, shared=True
    )
    return org


def set_status(harvest: Harvest, status: Harvest.Status) -> None:
    harvest.status = status
    harvest.save()


def clean_equipment_point(harvest: Harvest, org: Organization) -> Organization | None:
    form = HarvestForm(instance=harvest)
    form.cleaned_data = {
        'id': harvest.id,
        'status': harvest.status,
        'start_date': harvest.start_date,
        'end_date': harvest.end_date,
        'equipment_point': org,
    }
    return form.clean_equipment_point()


@pytest.mark.parametrize(
    'status, reserved',
    [(Harvest.Status.SCHEDULED, True), (Harvest.Status.SUCCEEDED, False)],
)
def test_make_reservation(harvest, equipment_point, client_core_user, status, reserved):
    set_status(harvest, status)

    client_core_user.post(
        reverse('harvest-make-reservation', args=[harvest.id]),
        {'org': equipment_point.actor_id},
        HTTP_REFERER='/',
    )

    assert harvest.equipment_reserved.exists() == reserved


def test_form_accepts_new_reservation_on_scheduled_harvest(harvest, equipment_point):
    set_status(harvest, Harvest.Status.SCHEDULED)

    assert clean_equipment_point(harvest, equipment_point) == equipment_point


def test_form_rejects_new_reservation_on_succeeded_harvest(harvest, equipment_point):
    set_status(harvest, Harvest.Status.SUCCEEDED)

    with pytest.raises(
        forms.ValidationError, match=re.escape(str(Harvest.CANNOT_MAKE_RESERVATION_MESSAGE))
    ):
        clean_equipment_point(harvest, equipment_point)


def test_form_keeps_existing_reservation_on_succeeded_harvest(harvest, equipment_point):
    harvest.equipment_reserved.set(equipment_point.equipment.all())
    set_status(harvest, Harvest.Status.SUCCEEDED)

    assert clean_equipment_point(harvest, equipment_point) == equipment_point
