import re
from datetime import datetime, date
from django.urls import reverse
from django.utils import timezone
from typing import Optional
from typeguard import typechecked
from django.conf import settings


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
