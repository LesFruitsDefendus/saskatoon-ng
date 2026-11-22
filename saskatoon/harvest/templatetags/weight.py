from typing import Optional

from django import template
from typeguard import typechecked

from harvest.utils import LB_TO_KG

register = template.Library()


@register.filter
@typechecked
def weight(lbs: Optional[float], unit: str = "lbs") -> str:
    if lbs is None:
        return ""
    return f"{to_unit(lbs, unit):.1f} {unit}"


@register.filter
@typechecked
def to_unit(lbs: float, unit: str = "lbs") -> float:
    """Converts a weight stored in lbs to the chosen unit"""
    if unit == "lbs":
        return lbs
    elif unit == "kg":
        return lbs * LB_TO_KG
    else:
        raise ValueError(f'Unexpected weight unit: "{unit}"')
