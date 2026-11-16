"""Tests for StatsView (harvest/api.py) and its serialized output.

Expected values are worked out by hand from the fixtures and reflect the
current behaviour of the stats methods, including known quirks (marked BUG),
so that later fix PRs have to update these tests deliberately.
"""

import pytest
from django.urls import reverse

from harvest.models import HarvestYield

pytestmark = pytest.mark.django_db


@pytest.fixture
def core_client(django_db_setup_with_fixtures, client_core_user):
    """Core user client with the shared test fixtures loaded (see conftest)"""
    return client_core_user


def get_stats(client, **params):
    response = client.get(reverse("statistics"), {"format": "json", **params})
    assert response.status_code == 200
    return response.json()


def fruit_rows(data):
    return sorted((row["harvests"], row["weight"]) for row in data["fruits"])


def test_stats_all_seasons(core_client):
    data = get_stats(core_client)

    assert data["season"] is None
    assert data["highlights"]["total_harvests"] == 2
    assert data["highlights"]["total_weight"] == 27
    # BUG: counts every distinct yield recipient, organizations included
    assert data["highlights"]["total_pickers"] == 5

    assert fruit_rows(data) == [(1, 7), (1, 8), (1, 12)]
    assert all(row["fruit_name"] for row in data["fruits"])

    # every lb lands in exactly one borough, and each harvest in one borough
    assert sum(row["weight"] for row in data["neighborhoods"]) == 27
    assert sum(row["harvests"] for row in data["neighborhoods"]) == 2


@pytest.mark.parametrize(
    "season, harvests, weight, pickers, fruits",
    [
        ("2026", 1, 15, 3, [(1, 7), (1, 8)]),
        ("2025", 1, 12, 3, [(1, 12)]),
    ],
)
def test_stats_by_season(core_client, season, harvests, weight, pickers, fruits):
    data = get_stats(core_client, season=season)

    assert data["season"] == season
    assert data["highlights"]["total_harvests"] == harvests
    assert data["highlights"]["total_weight"] == weight
    assert data["highlights"]["total_pickers"] == pickers
    assert fruit_rows(data) == fruits
    assert sum(row["weight"] for row in data["neighborhoods"]) == weight


def test_stats_empty_season(core_client):
    data = get_stats(core_client, season="2020")

    assert data["highlights"] == {
        "total_harvests": 0,
        "total_pickers": 0,
        "total_beneficiaries": 0,
        "total_weight": 0,
    }
    assert data["fruits"] == []
    assert data["neighborhoods"] == []
    assert data["beneficiaries"] == []
    assert data["pickers"] == []


def test_stats_page_renders(core_client):
    response = core_client.get(reverse("statistics"))

    assert response.status_code == 200
    content = response.content.decode()
    assert '<span class="count">27</span>' in content
    assert "27.0" not in content
    # one value from each table, so a wrong name in a template loop fails here
    assert "Green apples" in content
    assert "Plateau-Mont-Royal" in content
    assert "Les Fruits Défendus" in content
    assert "Pick Leader" in content


def test_stats_beneficiary_rows(core_client):
    data = get_stats(core_client)

    assert data["highlights"]["total_beneficiaries"] == 1
    assert data["beneficiaries"] == [
        {"beneficiary": "Les Fruits Défendus", "harvests": 1, "weight": 6},
    ]


def test_stats_picker_rows(core_client):
    pickers = {row.pop("picker"): row for row in get_stats(core_client)["pickers"]}

    assert pickers == {
        "Core Member": {
            "as_leader": 1,
            "requests": 2,
            "accepted": 0,
            "as_recipient": 1,
            "weight": 3,
        },
        "Michelle Delepeche": {
            "as_leader": 0,
            "requests": 1,
            "accepted": 0,
            "as_recipient": 1,
            "weight": 3,
        },
        # BUG: as_recipient counts yield rows; Nice Owner got 2 fruits from 1 harvest
        "Nice Owner": {
            "as_leader": 0,
            "requests": 0,
            "accepted": 0,
            "as_recipient": 2,
            "weight": 5,
        },
        "Pick Leader": {
            "as_leader": 1,
            "requests": 1,
            "accepted": 1,
            "as_recipient": 2,
            "weight": 10,
        },
    }


def test_stats_weight_is_whole_pounds(core_client):
    HarvestYield.objects.create(harvest_id=1, tree_id=9, total_in_lb=2.5, recipient_id=1)

    # sum_harvest_yields truncates with int(): 29.5 lbs reports as 29
    assert get_stats(core_client)["highlights"]["total_weight"] == 29


def test_stats_empty_season_shows_message(core_client):
    response = core_client.get(reverse("statistics"), {"season": "2020"})

    assert response.status_code == 200
    assert b"No harvests found" in response.content


def test_stats_seasons_only_in_html(core_client):
    assert "seasons" not in get_stats(core_client)
    assert b"2016" in core_client.get(reverse("statistics")).content
