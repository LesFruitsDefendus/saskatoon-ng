from django import template
from harvest.models import Harvest

register = template.Library()


@register.filter
def color(harvest_status: str) -> str:
    return {
        t[0].value: t[1] for t in [  # type: ignore
            (Harvest.Status.ORPHAN, "#ff2079"),  # btn-danger
            (Harvest.Status.ADOPTED, "#440bd4"),  # btn-primary
            (Harvest.Status.SCHEDULED, "#e8ad2b"),  # btn-warning
            (Harvest.Status.READY, "#2da4f0"),   # btn-info
            (Harvest.Status.SUCCEEDED, "#8bc34a"),  # btn-success
            (Harvest.Status.CANCELLED, "#666"),
        ]
    }.get(harvest_status, "#d4c7f9")  # btn-default


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
        idx = [s.value for s in statuses].index(status)  # type: ignore
    except ValueError:
        return 0

    return int(100/len(statuses))*(1 + idx)


@register.filter
def is_ready_or_succeeded(status: str) -> bool:
    return status in [
        s.value for s in [Harvest.Status.READY, Harvest.Status.SUCCEEDED]  # type: ignore
    ]
