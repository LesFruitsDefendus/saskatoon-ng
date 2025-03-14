import pytest
import json
from pathlib import Path

EXPECTATIONS_PATH = Path(__file__).parent.joinpath('expectations')


def get_json_url(page_name: str) -> str:
    return f"/{page_name}/?format=json"


@pytest.mark.django_db
def test_serializer_harvest_list(django_db_setup_with_fixtures, client_core_user):
    response = client_core_user.get(get_json_url('harvest'))
    assert response.status_code == 200

    harvest_list = json.loads(response.content)
    with open(EXPECTATIONS_PATH.joinpath('harvest_list.json'), 'r', encoding='utf-8') as expectation_file:
        expected_harvest_list = json.load(expectation_file)
        assert harvest_list == expected_harvest_list
