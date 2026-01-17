from datetime import datetime
from django.utils import timezone
import pytest

from django.conf import settings
from sitebase.utils import parse_naive_datetime, local_today


@pytest.mark.parametrize("unparsed", ["2025-12-18 16:00", "2025-12-18 18:00", "2025-12-19 15:00"])
def test_parse_naive_datetime_returns_right_timezone(unparsed):
    tzinfo = timezone.get_current_timezone()
    parsed = parse_naive_datetime(unparsed)

    # datetime.now(tz=tzinfo) is sometimes different from datetime.replace(tzinfo=tzinfo)
    assert parsed.tzinfo == datetime.now(tz=tzinfo).tzinfo


@pytest.mark.parametrize("unparsed", ["2025-12-18 16:00", "2025-12-18 18:00", "2025-12-19 15:00"])
def test_parse_naive_datetime_is_same_date(unparsed):
    parsed = parse_naive_datetime(unparsed, settings.DATETIME_INPUT_FORMATS[0])

    assert parsed.strftime(settings.DATETIME_INPUT_FORMATS[0]) == unparsed


def test_local_today() -> None:
    today = datetime.now(timezone.get_current_timezone())
    start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=today.tzinfo)

    assert start_of_day == local_today()
