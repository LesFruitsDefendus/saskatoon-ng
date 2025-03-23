import pytest
from pathlib import Path
from django.core.management import call_command
from django.contrib.auth import get_user_model


FIXTURE_PATH = Path(__file__).parent.parent.parent.joinpath('saskatoon/fixtures')
FIXTURE_SEQUENCE = [
    'auth-group',
    'member-city',
    'member-neighborhood',
    'member-state',
    'member-country',
    'member-actor',
    'member-person',
    'member-organization',
    'member-authuser',
    'harvest-treetype',
    'harvest-property',
    'harvest-equipmenttype',
    'harvest-equipment',
    'harvest-harvest',
    'harvest-harvestyield',
    'harvest-comment',
    'harvest-requestforparticipation',
    'sitebase-pagecontent'
]

AuthUser = get_user_model()


@pytest.fixture(scope="module")
def django_db_setup_with_fixtures(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        for fixture_name in FIXTURE_SEQUENCE:
            call_command('loaddata', FIXTURE_PATH.joinpath(f"{fixture_name}.json"))


@pytest.fixture
def client_core_user(client):
    # Revisit after we have 10 tests: whether it is necessary to reuse user from django fixtures
    user = AuthUser.objects.create_user(email="test@user.com", password="password1234")
    user.add_role('core')
    client.force_login(user)
    return client
