from typing import Literal, Optional

from django import template
from typeguard import typechecked

from harvest.utils import LB_TO_KG

register = template.Library()


@register.filter
@typechecked
def weight(lbs: Optional[float], unit: Literal["lb", "kg"] = "lb") -> str:
    if lbs is None:
        return ""
    if unit == "kg":
        return f"{lbs * LB_TO_KG:.1f} kg"
    return f"{lbs:.1f} lbs"
