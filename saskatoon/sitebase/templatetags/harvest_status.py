from django import template
from harvest.models import Harvest

register = template.Library()


@register.filter
def color(status: str) -> str:
    return {
        t[0].value: t[1] for t in [  # type: ignore
            (Harvest.Status.ORPHAN, "#333"),
            (Harvest.Status.ADOPTED, "#e7e0f9"),
            (Harvest.Status.SCHEDULED, "#e8ad2b"),
            (Harvest.Status.READY, "#2da4f0"),
            (Harvest.Status.SUCCEEDED, "#8bc34a"),
            (Harvest.Status.CANCELLED, "#f54952"),
        ]
    }.get(status, "#fff")


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
