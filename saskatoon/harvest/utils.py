from __future__ import annotations

from django.db.models import Q, Sum
from logging import getLogger
from typing import Optional
from datetime import datetime, timedelta
from typeguard import typechecked
import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile

from sitebase.utils import local_datetime
from saskatoon.settings import DEFAULT_RESERVATION_BUFFER

logger = getLogger('saskatoon')


def sum_harvest_yields(harvest_yield_qs):
    sum = harvest_yield_qs.aggregate(Sum("total_in_lb")).get("total_in_lb__sum")
    return int(sum) if sum is not None else None


def similar_properties(pending_property: Property):
    """Look for potential property/owner duplicates"""
    from harvest.models import Property

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


def resize_and_save_image(image, filename, image_resize_px=1200, field_name='image'):
    """Resize and save any uploaded image as a compressed JPG. Returns associated InMemoryUploadedFile.

    Arguments:
        image -- uploaded image object or file
        filename -- target file path in storage (MEDIA_ROOT not included)
        image_resize_px -- maximum allowed width/height in pixels
        field_name -- the form field name (default: 'image')
    """
    try:
        jpg_image = Image.open(image).convert('RGB')
        w0, h0 = jpg_image.size

        if max(w0, h0) > image_resize_px:
            if h0 > w0:  # portrait
                h1 = image_resize_px
                w1 = int(w0 * h1 / float(h0))
            else:  # landscape
                w1 = image_resize_px
                h1 = int(h0 * w1 / float(w0))
            jpg_image = jpg_image.resize((w1, h1), Image.Resampling.LANCZOS)

        image_io = BytesIO()
        jpg_image.save(image_io, format='JPEG', quality=90)
        image_io.seek(0)

        jpg_filename = os.path.splitext(filename)[0] + '.jpg'
        return InMemoryUploadedFile(
            file=image_io,
            field_name=field_name,
            name=jpg_filename,
            content_type='image/jpeg',
            size=image_io.tell(),
            charset=None,
        )
    except Exception as e:
        logger.error("%s: %s", type(e).__name__, str(e))
        return None
