import deal
from logging import getLogger
from django.db.models import Q, QuerySet
from datetime import timedelta, datetime
from secrets import choice
from typeguard import typechecked
from typing import Optional

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
def available_equipment_points(
    start: datetime,
    end: datetime,
    harvest: Optional[Harvest],
    buffer: timedelta = timedelta(hours=1),
) -> QuerySet[Organization]:
    """List all available equipment points for a given datetime range"""

    try:
        # A buffer gives pick leaders a bit of leeway in picking up and returning
        # the equipment, since some harvest sites can be further away
        start = start - buffer
        end = end + buffer

        # If a harvest has already reserved the equipment point and starts or ends during the
        # requested date range, then the equipment point is unavailable
        start_between = Q(harvest__start_date__gte=start) & Q(
            harvest__start_date__lte=end
        )
        end_between = Q(harvest__end_date__gte=start) & Q(harvest__end_date__lte=end)

        # We only want scheduled and ready harvests to impact availability
        is_active = Q(
            harvest__status__in=[Harvest.Status.SCHEDULED, Harvest.Status.READY]
        )

        not_conflicting = (start_between | end_between) & is_active

        # We need to exclude the present harvest from the results
        # so it doesnt conflict with itself
        id = getattr(harvest, "pk", None)
        not_itself = ~Q(harvest__pk=id)

        # To keep things simple, pick leaders must reserve entire equipment points.
        # But in the interest of allowing a more granular system in the future,
        # the harvest model still has a list of reserved equipment. This means that
        # any equipment reservation for a harvest will make that entire equipment
        # point reserved, even if part of it's equipment has not been added to the harvest
        conflicting_orgs = Equipment.objects.filter(
            not_itself & not_conflicting
        ).values("owner")

        return Organization.objects.filter(is_equipment_point=True).exclude(
            pk__in=conflicting_orgs
        )

    except Exception as _e:
        logger.warning(_e)
        return Organization.objects.none()
