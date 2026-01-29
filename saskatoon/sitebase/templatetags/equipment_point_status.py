from django import template

register = template.Library()


@register.filter
def reservation(status: str) -> str:
    return {
        t[0]: t[1]
        for t in [
            ('reserved', '#c01c28'),
            ('available', '#26a269'),
        ]
    }.get(status, '#000000')
