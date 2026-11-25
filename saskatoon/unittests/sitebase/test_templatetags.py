from datetime import timedelta

import pytest
from django.template.loader import render_to_string

from harvest.models import Harvest
from member.models import Organization
from sitebase.templatetags.harvest_status import (
    past_harvests_by_tree,
    upcoming_harvests,
    upcoming_harvests_by_tree,
)

EQUIPMENT_MAP = 'app/detail_views/harvest/equipment_map.html'
DISABLED = 'disabled data-placement="top"'


def equipment_map_context(org_status: str, **overrides):
    context = {
        'id': 1,
        'latitude': 45.5,
        'longitude': -73.6,
        'csrf_token': 'token',
        'equipment_point': None,
        'property': {'latitude': 45.5, 'longitude': -73.6},
        'equipment_points': [
            {
                'actor_id': 1,
                'civil_name': 'Org',
                'latitude': 45.5,
                'longitude': -73.6,
                'status': org_status,
                'is_equipment_point': True,
                'is_beneficiary': False,
            }
        ],
    }
    context.update(overrides)
    return context


@pytest.mark.parametrize(
    'harvest_status, org_status, disabled',
    [
        (Harvest.Status.SCHEDULED, Organization.EquipmentPointStatus.AVAILABLE, False),
        (Harvest.Status.READY, Organization.EquipmentPointStatus.AVAILABLE, False),
        (Harvest.Status.SUCCEEDED, Organization.EquipmentPointStatus.AVAILABLE, True),
        (Harvest.Status.SCHEDULED, Organization.EquipmentPointStatus.UNAVAILABLE, True),
        (Harvest.Status.CANCELLED, Organization.EquipmentPointStatus.AVAILABLE, True),
        (Harvest.Status.ORPHAN, Organization.EquipmentPointStatus.AVAILABLE, True),
    ],
)
def test_equipment_map_reserve_button(harvest_status, org_status, disabled):
    html = render_to_string(
        EQUIPMENT_MAP, equipment_map_context(org_status.value, status=harvest_status.value)
    )

    assert (DISABLED in html) is disabled


def test_equipment_map_missing_status_raises():
    """A missing/misspelled `status` must surface instead of silently enabling the button (#800)"""

    with pytest.raises(ValueError, match='Unexpected status'):
        render_to_string(
            EQUIPMENT_MAP, equipment_map_context(Organization.EquipmentPointStatus.AVAILABLE.value)
        )


@pytest.mark.parametrize(
    'offset, ended',
    [
        (timedelta(hours=-7), True),  # ended yesterday at 5pm
        (timedelta(0), False),
        (timedelta(hours=17), False),  # last day of the harvest has not ended yet
        (timedelta(days=1), False),
        (None, False),  # undated
    ],
)
def test_harvest_has_ended(frozen_today, offset, ended):
    end = frozen_today + offset if offset is not None else None

    assert Harvest(end_date=end).has_ended() is ended


def test_harvests_by_tree_split():
    past = {'end_date': '2026-11-19', 'ended': True, 'trees': ['apple']}
    upcoming = {'end_date': '2026-11-20', 'ended': False, 'trees': ['apple']}
    undated = {'end_date': None, 'ended': False, 'trees': ['apple']}
    other_tree = {'end_date': '2026-11-20', 'ended': False, 'trees': ['pear']}
    harvests = [past, upcoming, undated, other_tree]

    assert past_harvests_by_tree(harvests, 'apple') == [past]
    assert upcoming_harvests_by_tree(harvests, 'apple') == [upcoming]
    assert upcoming_harvests(harvests) == [upcoming, other_tree]
