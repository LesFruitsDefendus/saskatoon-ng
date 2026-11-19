"""Tests for StatsView (harvest/api.py) and its serialized output.

Where possible, tests check the stats against each other or against a change
made in the test, rather than against numbers worked out from the fixtures.
Known quirks are marked BUG so that later fix PRs have to update these tests
deliberately.
"""

import csv
import io
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.urls import reverse

from harvest.api import StatsExportView, StatsView
from harvest.models import Harvest, HarvestYield, RequestForParticipation as RFP
from harvest.serializers import STATS_TABLES
from member.models import Organization, Person

pytestmark = pytest.mark.django_db

# serializer field names for each table's columns, keyed by table key
TABLE_FIELDS = {
    key: [field for _label, field in columns] for key, _title, _source, columns in STATS_TABLES
}


@pytest.fixture(autouse=True)
def clear_cache():
    """The stats cache outlives each test's database, so start every test empty"""
    cache.clear()


@pytest.fixture
def core_client(db_with_fixtures, client_core_user):
    """Core user client with the baselines loaded for this test only"""
    return client_core_user


def get_stats(client, **params):
    response = client.get(reverse("statistics"), {"format": "json", **params})
    assert response.status_code == 200
    return response.json()


def get_export(client, **params):
    response = client.get(reverse("statistics-export"), params)
    assert response.status_code == 200
    return response


def table_rows(data, key):
    """A table's rows as dicts keyed by serializer field name"""
    table = next(t for t in data["tables"] if t["key"] == key)
    return [dict(zip(TABLE_FIELDS[key], row)) for row in table["rows"]]


def as_values(row):
    """Numbers compared by value, so "8.00" from the CSV equals 8.0 from the JSON"""
    values = []
    for cell in row:
        try:
            values.append(float(cell))
        except (TypeError, ValueError):
            values.append(cell)
    return values


def test_stats_all_seasons(core_client):
    data = get_stats(core_client)

    assert data["season"] is None
    # BUG: counts every distinct yield recipient, organizations included
    assert (
        data["highlights"]["total_pickers"]
        == len(table_rows(data, "picker")) + data["highlights"]["total_beneficiaries"]
    )


def test_stats_tables_match_highlights(core_client):
    data = get_stats(core_client)
    highlights = data["highlights"]

    total = pytest.approx(highlights["total_weight"])
    assert sum(row["weight"] for row in table_rows(data, "fruit")) == total
    assert sum(row["weight"] for row in table_rows(data, "neighborhood")) == total


def test_stats_seasons_add_up(core_client):
    everything = get_stats(core_client)["highlights"]

    per_season = []
    for season, _ in Harvest.SEASON_CHOICES:
        data = get_stats(core_client, season=season)
        assert data["season"] == str(season)
        per_season.append(data["highlights"])

    # total_pickers is left out: the same person can pick in several seasons
    assert sum(h["total_harvests"] for h in per_season) == everything["total_harvests"]
    assert sum(h["total_weight"] for h in per_season) == pytest.approx(everything["total_weight"])


def test_stats_empty_season(core_client):
    data = get_stats(core_client, season="2020")

    assert data["highlights"] == {
        "total_harvests": 0,
        "total_pickers": 0,
        "total_beneficiaries": 0,
        "total_weight": 0,
    }
    assert [t["key"] for t in data["tables"]] == list(TABLE_FIELDS)
    assert all(t["rows"] == [] for t in data["tables"])


def test_stats_page_renders(core_client):
    data = get_stats(core_client)
    response = core_client.get(reverse("statistics"))

    assert response.status_code == 200
    content = response.content.decode()
    assert f'<span class="count">{data["highlights"]["total_harvests"]}</span>' in content
    for table in data["tables"]:
        assert table["title"] in content
        assert table["rows"][0][0] in content


def existing_recipients():
    """Actors that already received fruit from a succeeded harvest"""
    return HarvestYield.objects.filter(harvest__status=Harvest.Status.SUCCEEDED).values(
        "recipient"
    )


def find_row(client, key, field, obj):
    return next(row for row in table_rows(get_stats(client), key) if row[field] == str(obj))


def add_yields(recipient, count, lbs):
    for _ in range(count):
        HarvestYield.objects.create(harvest_id=1, tree_id=9, total_in_lb=lbs, recipient=recipient)


def test_stats_beneficiary_rows(core_client):
    org = Organization.objects.filter(is_beneficiary=True, pk__in=existing_recipients()).first()
    assert org is not None, "fixtures need a beneficiary that received fruit"
    before = find_row(core_client, "beneficiary", "beneficiary", org)

    add_yields(org, count=2, lbs=3)
    after = find_row(core_client, "beneficiary", "beneficiary", org)

    # BUG: harvests counts yield rows, so 2 yields from 1 harvest adds 2
    assert after["harvests"] - before["harvests"] == 2
    assert after["weight"] - before["weight"] == pytest.approx(6)


def test_stats_picker_rows(core_client):
    person = Person.objects.filter(pk__in=existing_recipients()).first()
    assert person is not None, "fixtures need a person who received fruit"
    before = find_row(core_client, "picker", "picker", person)

    add_yields(person, count=2, lbs=3)
    RFP.objects.create(harvest_id=1, person=person, status=RFP.Status.DECLINED)
    after = find_row(core_client, "picker", "picker", person)

    # BUG: as_recipient counts yield rows, so 2 yields from 1 harvest adds 2
    assert after["as_recipient"] - before["as_recipient"] == 2
    assert after["weight"] - before["weight"] == pytest.approx(6)
    assert after["requests"] - before["requests"] == 1
    assert after["accepted"] == before["accepted"]


def test_stats_keeps_fractional_pounds(core_client):
    before = get_stats(core_client)["highlights"]["total_weight"]
    HarvestYield.objects.create(harvest_id=1, tree_id=9, total_in_lb=2.5, recipient_id=1)
    after = get_stats(core_client)["highlights"]["total_weight"]

    assert after - before == pytest.approx(2.5)


def test_stats_empty_season_shows_message(core_client):
    response = core_client.get(reverse("statistics"), {"season": "2020"})

    assert response.status_code == 200
    assert b"No harvests found" in response.content


def test_stats_includes_seasons(core_client):
    seasons = [choice[0] for choice in Harvest.SEASON_CHOICES]

    assert get_stats(core_client)["seasons"] == seasons
    assert str(seasons[0]) in core_client.get(reverse("statistics")).content.decode()


def test_stats_export_matches_page(core_client):
    data = get_stats(core_client)
    response = get_export(core_client)

    assert response["Content-Type"] == "text/csv; charset=utf-8"
    rows = [
        as_values(row) for row in csv.reader(io.StringIO(response.content.decode("utf-8-sig")))
    ]

    expected = []
    for table in data["tables"]:
        expected.append([table["title"]])
        expected.append(table["headers"])
        expected.extend(as_values(row) for row in table["rows"])
        expected.append([])
    assert rows == expected


def test_stats_export_filename(core_client):
    assert '_cumul' in get_export(core_client)["Content-Disposition"]
    assert '_2020.csv"' in get_export(core_client, season="2020")["Content-Disposition"]


def test_stats_export_reuses_page_data(core_client):
    get_stats(core_client)
    with patch.object(StatsExportView, "get_stats") as compute:
        get_export(core_client)

    compute.assert_not_called()


def test_stats_export_computes_without_page_load(core_client):
    with patch.object(
        StatsExportView, "get_stats", autospec=True, side_effect=StatsView.get_stats
    ) as compute:
        get_export(core_client)

    compute.assert_called_once()
