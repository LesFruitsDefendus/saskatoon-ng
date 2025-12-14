import re
from datetime import datetime, date
from django.urls import reverse
from django.utils import timezone
from typing import Optional, Any
from functools import reduce
from typeguard import typechecked

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


def parse_datetime(
        datetime_str: str,
        datetime_format: str = "%Y-%m-%d %H:%M"
) -> Optional[datetime]:
    """
    Parse a datetime string into a datetime object using the current timezone.

    Args:
        datetime_str (str): The datetime string to parse.
        datetime_format (str): The format to use for parsing (defaults to "%Y-%m-%d %H:%M")

    Returns:
        Optional[datetime]: A timezone-aware datetime object if parsing succeeds, otherwise None.
    """
    tzinfo = timezone.get_current_timezone()
    try:
        return datetime.strptime(datetime_str, datetime_format).replace(tzinfo=tzinfo)
    except ValueError:
        return None


def is_quill_html_empty(html: str) -> bool:
    return not len(re.sub(HTML_TAGS_REGEX, '', html))


@typechecked
def rgetattr(obj, attr: str, *args) -> Optional[Any]:
    """See https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects"""

    def _getattr(obj, attr: str) -> Optional[Any]:
        return getattr(obj, attr, *args)

    return reduce(_getattr, [obj] + attr.split('.'))
