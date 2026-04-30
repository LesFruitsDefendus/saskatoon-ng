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
    requested_start = start - buffer
    requested_end = end + buffer

    # If another harvest has already reserved the equipment available in the equipment
    # point and its datetime range overlaps, then the equipment point is unavailable.
    query = Q(status__in=Harvest.CAN_RESERVE_EQUIPMENT)

    # Dont include itself
    if harvest is not None:
        query = query & ~Q(pk=harvest.pk)

    start_between = Q(start_date__gte=requested_start, start_date__lte=requested_end)
    end_between = Q(end_date__gte=requested_start, end_date__lte=requested_end)
    surround = Q(start_date__lte=requested_start, end_date__gte=requested_end)

    conflicts = Harvest.objects.filter(query & (start_between | end_between | surround))
    booked_equipment = Equipment.objects.filter(pk__in=conflicts.values('equipment_reserved'))

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
