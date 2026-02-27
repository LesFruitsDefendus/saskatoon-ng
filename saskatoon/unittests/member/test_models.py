import pytest
from hypothesis import given, settings
from hypothesis.extra.django import TestCase, from_model
from datetime import timedelta, datetime, timezone

from member.models import (
    Country,
    State,
    City,
    Neighborhood,
    Actor,
    Person,
    AuthUser,
    Onboarding,
    Organization,
)

from harvest.models import Harvest, EquipmentType, Equipment

import unittests.member.strategies as member_st

# ruff tries to erase it because the weird way pytest applies
# fixtures is not recognised.
from unittests.member.fixtures import location  # noqa: F401

settings.register_profile("fast", max_examples=50)

# any tests executed before loading this profile will still use the
# default active profile of 100 examples.

settings.load_profile("fast")


class TestActor(TestCase):
    @given(actor=member_st.actor)
    def test_can_be_created(self, actor):
        assert isinstance(actor, Actor)


class TestOnboarding(TestCase):
    @given(onboarding=from_model(Onboarding))
    def test_can_be_created(self, onboarding):
        assert isinstance(onboarding, Onboarding)


class TestNeighborhood(TestCase):
    @given(neighborhood=from_model(Neighborhood))
    def test_can_be_created(self, neighborhood):
        assert isinstance(neighborhood, Neighborhood)


class TestState(TestCase):
    @given(state=from_model(State))
    def test_can_be_created(self, state):
        assert isinstance(state, State)


class TestCity(TestCase):
    @given(city=from_model(City))
    def test_can_be_created(self, city):
        assert isinstance(city, City)


class TestCountry(TestCase):
    @given(country=from_model(Country))
    def test_can_be_created(self, country):
        assert isinstance(country, Country)


class TestPerson(TestCase):
    @given(person=member_st.person)
    def test_can_be_created(self, person):
        assert isinstance(person, Person)


class TestOrganization(TestCase):
    @given(organization=member_st.organization)
    def test_can_be_created(self, organization):
        assert isinstance(organization, Organization)


class TestAuthUser(TestCase):
    @given(user=member_st.auth_user)
    def test_can_be_created(self, user):
        assert isinstance(user, AuthUser)


settings.load_profile("default")


@pytest.mark.django_db
def test_organization_get_harvests(location):  # noqa: F811
    org = Organization.objects.create(
        is_equipment_point=True, civil_name=" Test Equipment Point", **location
    )

    equip_type = EquipmentType.objects.create(name_fr="Type d'Equipement Test")

    equipment = Equipment.objects.create(
        type=equip_type,
        owner=org,
        shared=True,
    )

    tzinfo = timezone(timedelta(hours=-5))
    now = datetime.now(tzinfo)
    delta = timedelta(hours=2)

    harvest = Harvest.objects.create(start_date=now, end_date=now + delta)
    harvest.equipment_reserved.set([equipment])

    reservations = org.get_harvests()
    assert reservations.count() == 1
    first = reservations.first()
    assert first is not None
    assert first.id == harvest.id


@pytest.mark.django_db
def test_organization_longitude(location):  # noqa: F811
    long = -73.575174
    org = Organization.objects.create(
        civil_name=" Test org longitude",
        geom={"type": "Point", "coordinates": [long, 45.516465]},
        **location,
    )

    assert org.longitude == long


@pytest.mark.django_db
def test_organization_latitude(location):  # noqa: F811
    lat = 45.516465
    org = Organization.objects.create(
        civil_name=" Test org longitude",
        geom={"type": "Point", "coordinates": [-73.575174, lat]},
        **location,
    )

    assert org.latitude == lat
