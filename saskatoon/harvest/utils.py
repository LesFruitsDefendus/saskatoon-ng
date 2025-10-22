import deal
from django.db.models import Q, Sum, QuerySet
from logging import getLogger
from datetime import timedelta, datetime
from typeguard import typechecked

from harvest.models import Property, Equipment, Harvest
from member.models import Organization

logger = getLogger('saskatoon')


def sum_harvest_yields(harvest_yield_qs):
    sum = harvest_yield_qs.aggregate(Sum("total_in_lb")).get("total_in_lb__sum")
    return int(sum) if sum is not None else None


def similar_properties(pending_property: Property):
    """Look for potential property/owner duplicates"""

    p = pending_property
    if not p.pending:
        return Property.objects.none()

    query = Q()
    try:
        email = p.pending_contact_email
        if email:
            query |= Q(owner__person__auth_user__email=email)

        first_name = p.pending_contact_first_name
        family_name = p.pending_contact_family_name
        if first_name and family_name:
            q_first_name = Q(owner__person__first_name__icontains=first_name)
            q_family_name = Q(owner__person__family_name__icontains=family_name)
            query |= (q_first_name & q_family_name)

        phone = p.pending_contact_phone
        if phone:
            query |= Q(owner__person__phone=phone)

        # address match
        q0 = Q(street__icontains=p.street)
        q1 = Q(street_number__icontains=p.street_number)
        q2 = Q(postal_code__icontains=p.postal_code)
        q3 = Q(neighborhood=p.neighborhood)
        query |= q0 & q1 & (q2 | q3)  # TODO adjust, might be too stringent

        return Property.objects.filter(query).exclude(id=p.id).distinct()

    except Exception as _e:
        logger.warning("Could not find similar properties to <%s> (%s: %s)", p, type(_e), str(_e))
        return Property.objects.none()


@typechecked
def __valid_date_contract(start: datetime, end: datetime, buffer: timedelta) -> bool:
    try:
        start - buffer
        end + buffer

        return True
    except Exception:
        return False


@deal.pre(lambda _: _.start < _.end,
          message='end must be later then start')
@deal.pre(__valid_date_contract,
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
    """List all available equipment points for a harvest"""

    try:
        start = start - buffer
        end = end + buffer

        start_between = Q(harvest__start_date__gte=start) & Q(harvest__start_date__lte=end)
        end_between = Q(harvest__end_date__gte=start) & Q(harvest__end_date__lte=end)
        is_active = Q(harvest__status__in=[Harvest.Status.SCHEDULED, Harvest.Status.READY])

        conflicting_reservations = Equipment.objects.filter(
            (start_between | end_between) & is_active
        )

        return Organization.objects.filter(is_equipment_point=True).exclude(
            pk__in=conflicting_reservations.values("owner")
        )

    except Exception as _e:
        logger.warning(_e)
        return Organization.objects.none()
