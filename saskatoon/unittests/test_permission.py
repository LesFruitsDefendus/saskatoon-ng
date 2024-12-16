import pytest
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects
from typing import Union

STATIC_PAGES = ['calendar', 'property/create_public']
STATIC_PAGES_PERMISSION_REQUIRED = ['harvest', 'property', 'organization', 'community', 'equipment', 'stats']

User = get_user_model()


def get_url(page_name: str) -> str:
    return f"/{page_name}/"


@pytest.mark.django_db
def test_permission_static_pages_anonymous(client):
    for page in STATIC_PAGES:
        response = client.get(get_url(page))
        assert response.status_code == 200, f"Page: {page}"

    for page in STATIC_PAGES_PERMISSION_REQUIRED:
        url = get_url(page)
        response = client.get(url)
        assertRedirects(response, f"/login/?next={url}", msg_prefix=f"Page: {page}")


@pytest.mark.parametrize("auth_group, expected_status_codes",
                         [('core', 200),
                          ('pickleader', [200, 200, 200, 200, 200, 403]),
                          ('volunteer', 403),
                          ('owner', 403),
                          ('contact', 403)])
@pytest.mark.django_db
def test_permission_static_pages(client, auth_group, expected_status_codes: Union[int, list]):
    user = User.objects.create_user(email="test@user.com", password="password1234")
    user.add_role(auth_group)

    client.force_login(user)
    for i, page in enumerate(STATIC_PAGES_PERMISSION_REQUIRED):
        response = client.get(get_url(page))

        expected_status_code = expected_status_codes if isinstance(expected_status_codes, int) else expected_status_codes[i]
        assert response.status_code == expected_status_code, f"Auth group: {auth_group}, Page: {page}"
