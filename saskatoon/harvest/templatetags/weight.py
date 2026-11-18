from django import template

from harvest.utils import LB_TO_KG

register = template.Library()


@register.filter
def weight(lbs, unit="lb"):
    if lbs is None:
        return ""
    if unit == "kg":
        return f"{lbs * LB_TO_KG:.1f} kg"
    return f"{lbs:.1f} lbs"
