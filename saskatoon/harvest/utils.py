from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Optional, Any
from datetime import datetime, timedelta
from typeguard import typechecked
import os
import logging
from io import BytesIO
from PIL import Image

from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _

from sitebase.utils import local_datetime
from saskatoon.settings import DEFAULT_RESERVATION_BUFFER

if TYPE_CHECKING:
    from harvest.models import Property
logger = logging.getLogger('saskatoon')


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


def validate_image_upload(file):
    """Enforces allowed exrentions (jpg, jpeg, png) and caps upload size at 5MB."""
    allowed_extensions = ['jpg', 'jpeg', 'png']
    ext = file.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _("Unsuppoerted file format. Allowed formats: %(exts)s"),
            params={'exts': ', '.join(allowed_extensions).upper()},
        )

    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _("File size too large. Maximum allowed size is %(size)dMB."),
            params={'size': max_size_mb},
        )


def resize_and_save_image(
    image: Any, filename: str, image_resize_px: int = 1200, field_name: str = 'image'
) -> Optional[InMemoryUploadedFile]:
    """Resize and save any uploaded image as a compressed JPG. Returns associated InMemoryUploadedFile."""
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
