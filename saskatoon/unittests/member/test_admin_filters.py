import pytest
from django.test import RequestFactory
from django.contrib import admin
from django.db.models import QuerySet

from member.admin import OrganizationAdmin
from member.models import Organization, AuthUser
from unittests.member.fixtures import location, Location  # noqa: F401

ORG_URL = "http://localhost:8000/admin/member/organization/"


def make_org(loc: Location, with_geom: bool) -> Organization:
    return Organization.objects.create(
        civil_name=" Test org longitude",
        geom={"type": "Point", "coordinates": [-73.575174, 45.516465]} if with_geom else None,
        **loc,
    )


def query_admin_org(request) -> QuerySet[Organization]:
    admin_user = AuthUser.objects.create_superuser("admin", "password")

    modeladmin = OrganizationAdmin(Organization, admin.site)

    request.user = admin_user
    changelist = modeladmin.get_changelist_instance(request)

    return changelist.get_queryset(request)


@pytest.mark.django_db
def test_org_admin_filter_has_location(location):  # noqa: F811
    org = make_org(location, True)
    make_org(location, False)

    request_factory = RequestFactory()
    queryset = query_admin_org(request_factory.get(ORG_URL, {"geom": 1}))
    assert list(queryset) == [org]


@pytest.mark.django_db
def test_org_admin_filter_has_no_location(location):  # noqa: F811
    request_factory = RequestFactory()

    make_org(location, True)
    org = make_org(location, False)

    queryset = query_admin_org(request_factory.get(ORG_URL, {"geom": 0}))
    assert list(queryset) == [org]


@pytest.mark.django_db
def test_org_admin_filter_has_no_location_empty(location):  # noqa: F811
    request_factory = RequestFactory()

    make_org(location, False)

    queryset = query_admin_org(request_factory.get(ORG_URL, {"geom": 1}))
    assert list(queryset) == []
