from django import template
from harvest.models import RequestForParticipation as RFP

register = template.Library()


@register.filter
def rfp_color(status: str) -> str:
    return {
        t[0].value: t[1] for t in [  # type: ignore
            (RFP.Status.OBSOLETE, "#ff2079"),  # btn-danger
            (RFP.Status.DECLINED, "#e8ad2b"),  # btn-warning
            (RFP.Status.PENDING, "#2da4f0"),   # btn-info
            (RFP.Status.ACCEPTED, "#8bc34a"),  # btn-success
            (RFP.Status.CANCELLED, "#666"),  # btn-danger
        ]
    }.get(status, "#d4c7f9")  # btn-default


@register.filter
def rfp_status_display(status: str) -> str:
    for choice in RFP.Status.choices:
        if status == choice[0]:
            return choice[1]
    return ""
