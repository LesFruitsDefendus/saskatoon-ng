import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse

from harvest.models import PropertyImage
from unittests.conftest import FIXTURE_PATH, FIXTURE_SEQUENCE

AuthUser = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def fixture_data(db):
    for name in FIXTURE_SEQUENCE:
        call_command('loaddata', FIXTURE_PATH.joinpath(f"{name}.json"))


@pytest.fixture
def uploader(fixture_data):
    user = AuthUser.objects.create_user(email="uploader@test.com", password="password1234")
    user.add_role('pickleader')
    return user


@pytest.fixture
def other_user(fixture_data):
    user = AuthUser.objects.create_user(email="other@test.com", password="password1234")
    user.add_role('pickleader')
    return user


@pytest.fixture
def image(uploader):
    """An image from the fixtures, re-assigned to `uploader`."""
    img = PropertyImage.objects.get(pk=1)
    img.uploaded_by = uploader
    img.description = 'original'
    img.save(update_fields=['uploaded_by', 'description'])
    return img


def update_url(image):
    return reverse('property-image-update', args=[image.pk])


def delete_url(image):
    return reverse('property-image-delete', args=[image.pk])


def test_uploader_can_update(client, uploader, image):
    client.force_login(uploader)

    response = client.post(update_url(image), {'description': 'new text'})

    assert response.status_code == 302
    image.refresh_from_db()
    assert image.description == 'new text'


def test_core_user_can_update_others_image(client_core_user, image):
    response = client_core_user.post(update_url(image), {'description': 'moderated'})

    assert response.status_code == 302
    image.refresh_from_db()
    assert image.description == 'moderated'


def test_other_user_cannot_update(client, other_user, image):
    client.force_login(other_user)
    original = image.description

    response = client.post(update_url(image), {'description': 'hacked'})

    # The site's custom 403 handler renders with status 200, so this check is a little weaker
    assert response.status_code != 302
    image.refresh_from_db()
    assert image.description == 'original'


def test_uploader_can_delete(client, image, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    client.force_login(image.uploaded_by)

    response = client.post(delete_url(image))

    assert response.status_code == 302
    assert not PropertyImage.objects.filter(pk=image.pk).exists()


def test_other_user_cannot_delete(client, other_user, image):
    client.force_login(other_user)

    response = client.post(delete_url(image))

    # The site's custom 403 handler renders with status 200, so this check is a little weaker
    assert response.status_code != 302
    assert PropertyImage.objects.filter(pk=image.pk).exists()


@pytest.mark.parametrize('url_name', ['property-image-update', 'property-image-delete'])
def test_anonymous_is_redirected_to_login(client, image, url_name):
    response = client.post(reverse(url_name, args=[image.pk]))

    assert response.status_code == 302
    assert 'login' in response['Location']


@pytest.mark.parametrize('url_name', ['property-image-update', 'property-image-delete'])
def test_get_is_not_allowed(client, uploader, image, url_name):
    client.force_login(uploader)

    response = client.get(reverse(url_name, args=[image.pk]))

    assert response.status_code == 405
