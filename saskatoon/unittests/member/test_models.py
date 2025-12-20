from hypothesis import given, settings
from hypothesis.extra.django import TestCase, from_model

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

import unittests.member.strategies as member_st

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
