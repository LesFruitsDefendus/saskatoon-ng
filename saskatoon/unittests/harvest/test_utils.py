from datetime import timedelta, datetime
from django.utils import timezone

from harvest.utils import buffer_reservation_time


def test_buffer_reservation_time() -> None:
    date = datetime(2222, 5, 22, 18, 0, 0, 0, timezone.get_current_timezone())

    # Mainly I wanted to test that adding a negative timedelta would work
    delta = timedelta(hours=-1)

    assert "05:00 PM" == buffer_reservation_time(date, delta)
