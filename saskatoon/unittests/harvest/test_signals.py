import pytest
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from harvest.models import Harvest
from member.models import AuthUser


def test_crequest_middleware_is_installed():
    """CrequestMiddleware must run after AuthenticationMiddleware so request.user is set"""
    middleware = settings.MIDDLEWARE
    assert 'crequest.middleware.CrequestMiddleware' in middleware
    assert middleware.index('crequest.middleware.CrequestMiddleware') > middleware.index(
        'django.contrib.auth.middleware.AuthenticationMiddleware'
    )


@pytest.fixture
def current_request():
    request = RequestFactory().get('/')
    CrequestMiddleware.set_request(request)
    yield request
    CrequestMiddleware.del_request()


@pytest.mark.django_db
def test_harvest_changed_by_is_set_from_request(current_request):
    user = AuthUser.objects.create_user(email="editor@example.com", password="password1234")
    current_request.user = user

    harvest = Harvest.objects.create()

    harvest.refresh_from_db()
    assert harvest.changed_by == user


@pytest.mark.django_db
def test_harvest_changed_by_is_cleared_for_anonymous(current_request):
    current_request.user = AnonymousUser()

    harvest = Harvest.objects.create()

    harvest.refresh_from_db()
    assert harvest.changed_by is None
