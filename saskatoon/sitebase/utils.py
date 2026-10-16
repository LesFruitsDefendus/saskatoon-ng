import re
from datetime import datetime, date
from django.urls import reverse
from django.utils import timezone
from typing import Optional, Any, Callable
from typeguard import typechecked
from django.conf import settings
from django.utils.translation import get_language, gettext_lazy as _
from django.contrib.humanize.templatetags.humanize import ordinal as django_ordinal
import os
from io import BytesIO
from PIL import Image
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from logging import getLogger

logger = getLogger('saskatoon')

HTML_TAGS_REGEX = re.compile(r'<.*?>|\s+')


def get_filter_context(viewset, basename=None):
    '''create filters dictionary for list views
    @param {obj} viewset: ModelViewSet subclass instance
    @returns {dic} filters: filters template dictionary
    '''
    f = viewset.filterset_class(viewset.request.GET, viewset.queryset)
    dic = {'form': f.form}
    if any(field in viewset.request.GET for field in set(f.get_fields())):
        dic['reset'] = reverse(
            "{}-list".format(basename if basename is not None else viewset.basename)
        )
    return dic


def renderer_format_needs_json_response(request) -> bool:
    """Checks if the template renderer format is json or the DRF browsable api
    which require the response to be plain json.
    Default request format is html.
    """
    return request.accepted_renderer.format in ('json', 'api')


def local_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    return dt.astimezone(timezone.get_current_timezone())


def to_datetime(date: Optional[date]) -> Optional[datetime]:
    if date is None:
        return None
    return local_datetime(datetime.combine(date, datetime.min.time()))


@typechecked
def local_today() -> datetime:
    """Return the start of day datetime for a localized datetime.now()"""
    today = datetime.now(timezone.get_current_timezone())
    return today.replace(hour=0, minute=0, second=0, microsecond=0)


@typechecked
def parse_naive_datetime(
    datetime_str: str, datetime_format: str = settings.DATETIME_INPUT_FORMATS[0]
) -> Optional[datetime]:
    """
    Parse a naive datetime string into a datetime object using the current timezone.
    """
    tzinfo = timezone.get_current_timezone()

    # For some arcane reason, passing tzinfo to datetime.replace gives us -5:18, if we pass it
    # to datetime.now first then use it's timezone with replace, we get -5:00 as expected.
    now = datetime.now(tz=tzinfo)

    try:
        return datetime.strptime(datetime_str, datetime_format).replace(tzinfo=now.tzinfo)
    except ValueError:
        return None


def is_quill_html_empty(html: str) -> bool:
    return not len(re.sub(HTML_TAGS_REGEX, '', html))


@typechecked
def maybe(val: Any, default: Optional[Any] = None, callable: Callable[[Any], Any] = lambda b: b):
    if val is not None:
        return callable(val)

    return default


def french_ordinal(n: int) -> str:
    # If French, use French ordinal rules (er / e)
    if get_language().startswith('fr'):
        return f"{n}{'er' if n == 1 else 'ème'}"

    return str(django_ordinal(n))


def validate_image_size(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _("File size too large. Maximum allowed size is %(size)dMB."),
            params={'size': max_size_mb},
        )


IMAGE_VALIDATORS = (
    FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
    validate_image_size,
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
