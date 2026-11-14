from __future__ import annotations

import os
from datetime import datetime, timedelta
from io import BytesIO
from logging import getLogger
from typing import TYPE_CHECKING, Any, Optional

from django.apps import apps
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q, Sum
from PIL import Image, ImageOps
from typeguard import typechecked

if TYPE_CHECKING:
    from harvest.models import Property
from saskatoon.settings import DEFAULT_RESERVATION_BUFFER
from sitebase.utils import local_datetime

logger = getLogger('saskatoon')


def sum_harvest_yields(harvest_yield_qs):
    sum = harvest_yield_qs.aggregate(Sum("total_in_lb")).get("total_in_lb__sum")
    return int(sum) if sum is not None else None


def similar_properties(pending_property: Property):
    """Look for potential property/owner duplicates"""
    Property = apps.get_model('harvest', 'Property')
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


def _flatten_to_rgb(img: Image.Image) -> Image.Image:
    """Convert to RGB, putting transparent areas on white (not black)."""
    has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
    if not has_alpha:
        return img.convert('RGB')

    rgba = img.convert('RGBA')
    background = Image.new('RGB', rgba.size, (255, 255, 255))
    background.paste(rgba, mask=rgba.getchannel('A'))
    return background


def resize_and_save_image(
    image: Any, filename: str, image_resize_px: int = 1080, field_name: str = 'image'
) -> Optional[InMemoryUploadedFile]:
    """Resize and save any uploaded image as a compressed JPG. Returns associated InMemoryUploadedFile."""
    try:
        with Image.open(image) as src:
            img = ImageOps.exif_transpose(src)
            img = _flatten_to_rgb(img)
            img.thumbnail((image_resize_px, image_resize_px), Image.Resampling.LANCZOS)

            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)

        file_size = buffer.getbuffer().nbytes
        buffer.seek(0)

        return InMemoryUploadedFile(
            file=buffer,
            field_name=field_name,
            name=os.path.splitext(filename)[0] + '.jpg',
            content_type='image/jpeg',
            size=file_size,
            charset=None,
        )
    except Exception:
        logger.exception("Could not process uploaded image %s", filename)
        return None
