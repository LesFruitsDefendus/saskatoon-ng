import deal
from logging import getLogger
from django.db.models import Q, QuerySet
from datetime import timedelta, datetime
from secrets import choice
from typeguard import typechecked

from member.models import AuthUser, Organization
from harvest.models import Equipment, Harvest

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
def _valid_date_contract(start: datetime, end: datetime, buffer: timedelta) -> bool:
    """ If any of these result in an OverflowError then the
          the condition is broken. We catch the exception so
          that Deal can report the contract violation correctly """
    try:
        start - buffer
        end + buffer

        return True
    except Exception:
        return False


@deal.pre(lambda _: _.start < _.end,
          message='end must be later then start')
@deal.pre(_valid_date_contract,
          message='Substracting the buffer from the start date and '
          'adding the buffer to the end date must result in valid dates')
@deal.pre(lambda _: _.start.tzinfo is not None and _.end.tzinfo is not None,
          message='start and end must be offset aware')
@typechecked
def available_equipment_points(
    start: datetime,
    end: datetime,
    buffer: timedelta
) -> QuerySet[Organization]:
    """List all available equipment points for a given datetime range"""

    try:
        start = start - buffer
        end = end + buffer

        start_between = Q(harvest__start_date__gte=start) & Q(harvest__start_date__lte=end)
        end_between = Q(harvest__end_date__gte=start) & Q(harvest__end_date__lte=end)
        is_active = Q(harvest__status__in=[Harvest.Status.SCHEDULED, Harvest.Status.READY])

        conflicting_reservations = Equipment.objects.filter(
            (start_between | end_between) & is_active
        ).values("owner")

        return Organization.objects.filter(is_equipment_point=True).exclude(
            pk__in=conflicting_reservations
        )

    except Exception as _e:
        logger.warning(_e)
        return Organization.objects.none()
