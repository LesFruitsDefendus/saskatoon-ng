from datetime import datetime
from django.utils import timezone
import pytest

from sitebase.utils import parse_naive_datetime, rgetattr


@pytest.mark.parametrize("unparsed", ["2025-12-18+16:00", "2025-12-18+18:00", "2025-12-19+15:00"])
def test_parse_naive_datetime(unparsed):
    tzinfo = timezone.get_current_timezone()
    parsed = parse_naive_datetime(unparsed)

    # datetime.now(tz=tzinfo) is sometimes different from datetime.replace(tzinfo=tzinfo)
    assert parsed.tzinfo == datetime.now(tz=tzinfo).tzinfo


class Deepest:
    bottom = "value"


class Deep:
    deepest = Deepest()


class Surface:
    deep = Deep()


class Empty:
    pass


def test_rgetattr():
    surface = Surface()

    assert rgetattr(surface, 'deep.deepest.bottom', str, None) == "value"


def test_rgetattr_missing_key():
    surface = Surface()
    surface.deep.deepest = Empty()

    assert rgetattr(surface, 'deep.deepest.bottom', str, None) is None


def test_rgetattr_missing_intermediate_key():
    surface = Surface()

    surface.deep = Empty()

    assert rgetattr(surface, 'deep.deepest.bottom', str, None) is None
