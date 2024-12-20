import pytest
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects

AUTH_GROUPS = ['core', 'pickleader', 'volunteer', 'owner', 'contact']

STATIC_PAGES_PUBLIC = ['calendar', 'property/create_public']
STATIC_PAGES_PERMISSION_REQUIRED = {
    'harvest': ['core', 'pickleader'],
    'property': ['core', 'pickleader'],
    'organization': ['core', 'pickleader'],
    'community': ['core', 'pickleader'],
    'equipment': ['core', 'pickleader'],
    'stats': ['core']
}

AuthUser = get_user_model()


def get_url(page_name: str) -> str:
    return f"/{page_name}/"


@pytest.mark.django_db
def test_permission_static_pages_anonymous(client):
    for page in STATIC_PAGES_PUBLIC:
        response = client.get(get_url(page))
        assert response.status_code == 200, f"Page: {page}"

    for page in STATIC_PAGES_PERMISSION_REQUIRED:
        url = get_url(page)
        response = client.get(url)
        assertRedirects(response, f"/login/?next={url}", msg_prefix=f"Page: {page}")


@pytest.mark.parametrize("auth_group", AUTH_GROUPS)
@pytest.mark.django_db
def test_permission_static_pages_logged_in(client, auth_group):
    user = AuthUser.objects.create_user(email="test@user.com", password="password1234")
    user.add_role(auth_group)

    client.force_login(user)
    for page, permitted_groups in STATIC_PAGES_PERMISSION_REQUIRED.items():
        response = client.get(get_url(page))

        expected_status_code = 200 if (auth_group in permitted_groups) else 403
        assert response.status_code == expected_status_code, f"Auth group: {auth_group}, Page: {page}"
