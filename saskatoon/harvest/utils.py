from django.db.models import Q, Sum
from logging import getLogger
from typing import Optional
from datetime import datetime, timedelta
from typeguard import typechecked

from harvest.models import Property
from sitebase.utils import local_datetime
from saskatoon.settings import DEFAULT_RESERVATION_BUFFER

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
            query |= q_first_name & q_family_name

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
def buffer_reservation_time(
    time: Optional[datetime],
    buffer: timedelta = timedelta(hours=DEFAULT_RESERVATION_BUFFER),
) -> Optional[str]:
    if (raw_time := time) is None or (local_time := local_datetime(raw_time + buffer)) is None:
        return None

    return local_time.strftime("%I:%M %p")
