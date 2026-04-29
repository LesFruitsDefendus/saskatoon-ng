import deal
from logging import getLogger
from django.db.models import Q, QuerySet
from datetime import timedelta, datetime
from secrets import choice
from typeguard import typechecked
from typing import Optional, Union

from member.models import AuthUser, Organization
from harvest.models import Equipment, Harvest
from saskatoon.settings import DEFAULT_RESERVATION_BUFFER

logger = getLogger('saskatoon')


def make_random_password(length=10) -> str:
    allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(choice(allowed_chars) for i in range(length))


def reset_password(user: AuthUser) -> str:
    password = make_random_password(12)
    user.set_password(password)
    user.has_temporary_password = True
    user.save()
    return password


@typechecked
def _valid_date_contract(_) -> bool:
    """If any of these result in an OverflowError then the
    the condition is broken. We catch the exception so
    that Deal can report the contract violation correctly"""
    try:
        _.start - _.buffer
        _.end + _.buffer

        return True
    except Exception:
        return False


@deal.pre(lambda _: _.start < _.end, message="end must be later then start")
@deal.pre(
    _valid_date_contract,
    message="Substracting the buffer from the start date and "
    "adding the buffer to the end date must result in valid dates",
)
@deal.pre(
    lambda _: _.start.tzinfo is not None and _.end.tzinfo is not None,
    message="start and end must be offset aware",
)
@typechecked
def get_available_equipment_points(
    start: datetime,
    end: datetime,
    harvest: Optional[Harvest] = None,
    buffer: timedelta = timedelta(hours=DEFAULT_RESERVATION_BUFFER),
) -> QuerySet[Organization]:
    """List all available equipment points for a given datetime range"""

    # A buffer gives pick leaders a bit of leeway in picking up and returning
    # the equipment, since some harvest sites can be further away
    start = start - buffer
    end = end + buffer

    # If another harvest has already reserved the equipment available in the equipment
    # point and its datetime range overlaps, then the equipment point is unavailable.
    has_datetimes = Q(harvest__status__in=Harvest.ALLOWED_TO_RESERVE)
    start_between = Q(harvest__start_date__gte=start, harvest__start_date__lte=end)
    end_between = Q(harvest__end_date__gte=start, harvest__end_date__lte=end)
    surround = Q(harvest__start_date__lte=start, harvest__end_date__gte=end)

    booked_equipment = Equipment.objects.filter(
        has_datetimes & (start_between | end_between | surround)
    )

    # Make sure harvest doesn't conflict with itself
    if harvest is not None:
        has_datetimes = Q(status__in=Harvest.ALLOWED_TO_RESERVE)
        start_between = Q(start_date__gte=start, start_date__lte=end)
        end_between = Q(end_date__gte=start, end_date__lte=end)
        surround = Q(start_date__lte=start, end_date__gte=end)
        same_reservation = Q(equipment_reserved__pk__in=harvest.equipment_reserved.all())
        different = ~Q(pk=harvest.pk)

        harvests = Harvest.objects.filter(
            different & has_datetimes & (start_between | end_between | surround) & same_reservation
        )

        if harvests.count() == 0:
            booked_equipment = booked_equipment.exclude(harvest__pk=harvest.pk)

    return Organization.objects.filter(is_equipment_point=True).exclude(
        pk__in=booked_equipment.values('owner')
    )


@typechecked
def is_equipment_point_available(
    org: Organization,
    start: Union[datetime, None],
    end: Union[datetime, None],
    harvest: Optional[Harvest] = None,
) -> bool:
    """Check if an equipment point is available for a given time range"""

    if not org.is_equipment_point or start is None or end is None:
        return False

    return get_available_equipment_points(start, end, harvest).filter(pk=org.pk).exists()
