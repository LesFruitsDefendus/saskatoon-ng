from django import template

register = template.Library()


@register.filter
def reservation(status: str) -> str:
    return {
        t[0]: t[1]
        for t in [
            ('reserved', "/static/js/map/icon/marker-reserved.svg"),
            ('available', "/static/js/map/icon/marker-available.svg"),
        ]
    }.get(status, "/static/js/map/icon/marker-default.svg")
