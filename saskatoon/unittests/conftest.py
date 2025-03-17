import pytest
from pathlib import Path
from django.core.management import call_command
from django.contrib.auth import get_user_model


FIXTURES_FILE = Path(__file__).parent.joinpath('testing_db.json')

AuthUser = get_user_model()


@pytest.fixture(scope="module")
def django_db_setup_with_fixtures(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', FIXTURES_FILE)


@pytest.fixture
def client_core_user(client):
    user = AuthUser.objects.create_user(email="test@user.com", password="password1234")
    user.add_role('core')
    client.force_login(user)
    return client
