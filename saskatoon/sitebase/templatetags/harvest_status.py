from django import template
from harvest.models import Harvest

register = template.Library()


@register.filter
def color(status: str) -> str:
    return {
        t[0].value: t[1] for t in [
            (Harvest.Status.ORPHAN, "#333"),
            (Harvest.Status.ADOPTED, "#CCC"),
            (Harvest.Status.SCHEDULED, "#FFC107"),
            (Harvest.Status.READY, "#2196F3"),
            (Harvest.Status.SUCCEEDED, "#4CAF50"),
            (Harvest.Status.CANCELLED, "#F44336"),
        ]
    }.get(status, "#FFF")


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

    return int(100/len(statuses))*(1 + idx)
