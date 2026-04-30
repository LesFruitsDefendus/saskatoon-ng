from django import template
from typeguard import typechecked

from harvest.models import Harvest

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


@typechecked
def harvest_filter(harvest_status: str, size: str) -> str:
    return {
        t[0].value: t[1]
        for t in [
            (
                Harvest.Status.ORPHAN,
                '<span class="glyphicon glyphicon-tree-deciduous fa-lg"></span>',
            ),
            (
                Harvest.Status.ADOPTED,
                '<span class="glyphicon glyphicon-tree-deciduous fa-lg"></span>',
            ),
            (
                Harvest.Status.SCHEDULED,
                '<span class="fa fa-shopping-basket fa-lg"></span>',
            ),
            (Harvest.Status.READY, '<span class="fa fa-shopping-basket fa-lg"></span>'),
            (Harvest.Status.SUCCEEDED, '<span class="glyphicon glyphicon-apple fa-lg"></span>'),
            (Harvest.Status.CANCELLED, '<span class="glyphicon glyphicon-apple fa-lg"></span>'),
        ]
    }.get(
        harvest_status, '<span class="glyphicon glyphicon-tree-deciduous fa-lg"></span>'
    )  # btn-default


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
