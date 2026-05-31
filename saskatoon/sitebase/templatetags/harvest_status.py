from django import template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from typeguard import typechecked
from typing import Optional, Callable

from harvest.models import Harvest
from sitebase.utils import parse_naive_datetime, local_today
from saskatoon.settings import DATE_INPUT_FORMATS

register = template.Library()


@register.filter
@typechecked
def color(harvest_status: str) -> str:
    return {
        t[0].value: t[1]
        for t in [
            (Harvest.Status.ORPHAN, "saskatoon-warning"),
            (Harvest.Status.ADOPTED, "saskatoon-info"),
            (Harvest.Status.SCHEDULED, "saskatoon-warning"),
            (Harvest.Status.READY, "saskatoon-info"),
            (Harvest.Status.SUCCEEDED, "saskatoon-success"),
            (Harvest.Status.CANCELLED, "saskatoon-danger"),
        ]
    }.get(harvest_status, "saskatoon-success")


def make_icon(icon: Callable[[str], str], size: str, mode: str):
    if mode == 'stack':
        return '<span class="fa-stack fa-2x fa-{size}"><i class="fa-solid fa-circle fa-stack-2x" style="color: white;"></i>{icon}</span>'.format(
            size=size, icon=icon('stack-1x')
        )

    return icon(size)


@typechecked
def tree_icon(size: str):
    return '<i class="glyphicon glyphicon-tree-deciduous fa-{size}"></i>'.format(size=size)


@typechecked
def apple_icon(size: str):
    return '<i class="glyphicon glyphicon-apple fa-{size}"></i>'.format(size=size)


@typechecked
def shopping_basket_icon(size: str):
    return '<i class="fa-shopping-basket fa-solid fa-{size}"></i>'.format(size=size)


@typechecked
def close_icon(size: str):
    return '<i class="fa-close fa-solid fa-{size}"></i>'.format(size=size)


@typechecked
def harvest_filter(harvest_status: str, size: str, mode: str = 'flat') -> str:
    return {
        t[0].value: t[1]
        for t in [
            (
                Harvest.Status.ORPHAN,
                make_icon(tree_icon, size, mode),
            ),
            (
                Harvest.Status.ADOPTED,
                make_icon(tree_icon, size, mode),
            ),
            (
                Harvest.Status.SCHEDULED,
                make_icon(shopping_basket_icon, size, mode),
            ),
            (
                Harvest.Status.READY,
                make_icon(shopping_basket_icon, size, mode),
            ),
            (
                Harvest.Status.SUCCEEDED,
                make_icon(apple_icon, size, mode),
            ),
            (
                Harvest.Status.CANCELLED,
                make_icon(close_icon, size, mode),
            ),
        ]
    }.get(
        harvest_status,
        make_icon(tree_icon, size, mode),
    )


@register.filter
@typechecked
def harvest_icon(harvest_status: str) -> str:
    return harvest_filter(harvest_status, 'lg')


@register.filter
@typechecked
def harvest_icon_hover(harvest_status: str) -> str:
    return harvest_filter(harvest_status, 'xl')


@register.filter
@typechecked
def harvest_icon_stacked(harvest_status: str) -> str:
    return harvest_filter(harvest_status, 'lg', 'stack')


@register.filter
@typechecked
def harvest_icon__stacked_hover(harvest_status: str) -> str:
    return harvest_filter(harvest_status, 'xl', 'stack')


@register.filter
@typechecked
def progress(status: str) -> int:
    statuses = [
        Harvest.Status.ADOPTED,
        Harvest.Status.SCHEDULED,
        Harvest.Status.READY,
        Harvest.Status.CANCELLED,
        Harvest.Status.SUCCEEDED,
    ]

    try:
        idx = [s.value for s in statuses].index(status)
    except ValueError:
        return 0

    return int(100 / len(statuses)) * (1 + idx)


@register.filter
@typechecked
def is_ready_or_succeeded(status: str) -> bool:
    return status in [s.value for s in [Harvest.Status.READY, Harvest.Status.SUCCEEDED]]


@register.filter
@typechecked
def next_harvest_date(harvest):
    if harvest['date_range'] not in [None, '']:
        return harvest['date_range']

    return harvest['start_date']


@register.filter
@typechecked
def past_harvest(harvest):
    start = parse_naive_datetime(harvest['start_date'], DATE_INPUT_FORMATS[0])
    end = parse_naive_datetime(harvest['end_date'], DATE_INPUT_FORMATS[0])
    today = local_today()

    if start is None or end is None:
        return 'time parsing error'

    if today > start and today < end:
        return 'upcoming'

    if today < start:
        return 'upcoming'

    return 'past'


@register.filter
@typechecked
def past_harvests_by_tree(harvests, tree):
    return list(filter(lambda h: tree in h['trees'] and past_harvest(h) == 'past', harvests))


@register.filter
@typechecked
def upcoming_harvests_by_tree(harvests, tree):
    return list(filter(lambda h: tree in h['trees'] and past_harvest(h) == 'upcoming', harvests))


@register.filter
@typechecked
def upcoming_harvests(harvests):
    return list(filter(lambda h: past_harvest(h) == 'upcoming', harvests))


@register.filter
@typechecked
def harvest_link_attributes(harvest):
    pick_leader = (
        harvest['pick_leader']['name'] if harvest['pick_leader'] is not None else _("Orphan")
    )
    url = reverse('harvest-detail', args=[harvest['id']])

    return (
        'data-placement="top" data-toggle="tooltip" href="'
        + url
        + '" title="#'
        + str(harvest['id'])
        + ': '
        + next_harvest_date(harvest)
        + ' '
        + pick_leader
        + '"'
    )


@register.filter
@typechecked
def harvest_status_attributes(status: Optional[str], direction: str = "bottom") -> str:
    default = ''

    if status is None:
        return default

    help_text = {
        t[0]: t[1]
        for t in [
            (
                Harvest.Status.ADOPTED.value,
                _("Harvest has been adopted, but still needs to be scheduled"),
            ),
            (
                Harvest.Status.SCHEDULED.value,
                _("Harvest has been scheduled and has room for more pickers"),
            ),
            (
                Harvest.Status.READY.value,
                _("Harvest is ready to start, there are no more empty spots for pickers"),
            ),
            (
                Harvest.Status.CANCELLED.value,
                _("Harvest is cancelled, it will need to be rescheduled by the pick leader"),
            ),
            (
                Harvest.Status.SUCCEEDED.value,
                _("Harvest is finished and fruits have been harvested"),
            ),
            (Harvest.Status.ORPHAN.value, _("Harvest needs a pick leader to adopt it")),
        ]
    }.get(status, default)

    return 'data-placement="' + direction + '" data-toggle="tooltip" title="' + help_text + '"'
