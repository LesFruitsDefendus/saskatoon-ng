from django import template
from harvest.models import Harvest

register = template.Library()


@register.filter
def color(harvest_status: str) -> str:
    return {
        t[0].value: t[1]
        for t in [
            (Harvest.Status.ORPHAN, "#c01c28"),
            (Harvest.Status.ADOPTED, "#000"),
            (Harvest.Status.SCHEDULED, "#2da4f0"),
            (Harvest.Status.READY, "#e8ad2b"),
            (Harvest.Status.SUCCEEDED, "#440bd4"),
            (Harvest.Status.CANCELLED, "#c01c28"),
        ]
    }.get(harvest_status, "#666")  # btn-default


@register.filter
def harvest_icon(harvest_status: str) -> str:
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
                '<span class="glyphicon glyphicon-tree-deciduous fa-lg"></span>',
            ),
            (Harvest.Status.READY, '<span class="glyphicon glyphicon-apple fa-lg"></span>'),
            (Harvest.Status.SUCCEEDED, '<span class="glyphicon glyphicon-apple fa-lg"></span>'),
            (Harvest.Status.CANCELLED, '<span class="glyphicon glyphicon-apple fa-lg"></span>'),
        ]
    }.get(
        harvest_status, '<span class="glyphicon glyphicon-tree-deciduous fa-lg"></span>'
    )  # btn-default


@register.filter
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
def is_ready_or_succeeded(status: str) -> bool:
    return status in [s.value for s in [Harvest.Status.READY, Harvest.Status.SUCCEEDED]]
