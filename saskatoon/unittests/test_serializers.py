import pytest
import json
from pathlib import Path

BASELINES_PATH = Path(__file__).parent.joinpath('baselines')
ENDPOINT_BASELINE_PAIRS = [
    ('harvest', 'harvest_list.json'),
    ('harvest/1', 'harvest_detail.json'),
    ('property', 'property_list.json'),
    ('property/3', 'property_detail.json'),
    ('organization', 'organization_list.json'),
    ('organization/2', 'organization_detail.json'),
    ('community', 'community_list.json'),
    ('equipment-point', 'equipment-point_list.json')
]


def get_json_url(page_name: str) -> str:
    return f"/{page_name}/?format=json"


@pytest.mark.parametrize("endpoint, baseline_filename", ENDPOINT_BASELINE_PAIRS)
@pytest.mark.django_db
def test_serializers(django_db_setup_with_fixtures, client_core_user, endpoint, baseline_filename):
    response = client_core_user.get(get_json_url(endpoint))
    assert response.status_code == 200

    response_json = json.loads(response.content)
    with open(BASELINES_PATH.joinpath(baseline_filename), 'r', encoding='utf-8') as baseline_file:
        assert response_json == json.load(baseline_file)

    ''' Generate new baseline files
    with open(BASELINES_PATH.joinpath(baseline_filename), 'w', encoding='utf-8') as baseline_file:
        json.dump(response_json, baseline_file, ensure_ascii=False, indent=4)
    '''
