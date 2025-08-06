import re

from datetime import datetime, date
from django.urls import reverse
from django.utils import timezone
from typing import Optional

HTML_TAGS_REGEX = re.compile('<.*?>|\s+')


def get_filter_context(viewset, basename=None):
    ''' create filters dictionary for list views
    @param {obj} viewset: ModelViewSet subclass instance
    @returns {dic} filters: filters template dictionary
    '''
    f = viewset.filterset_class(viewset.request.GET, viewset.queryset)
    dic = {'form': f.form}
    if any(field in viewset.request.GET for field in set(f.get_fields())):
        dic['reset'] = reverse("{}-list".format(
            basename if basename is not None else viewset.basename
        ))
    return dic


def renderer_format_needs_json_response(request) -> bool:
    """ Checks if the template renderer format is json or the DRF browsable api
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


def is_quill_html_empty(html: str) -> bool:
    return not len(re.sub(HTML_TAGS_REGEX, '', html))
