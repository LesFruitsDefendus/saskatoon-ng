from django import template
from typeguard import typechecked
from typing import Optional

from harvest.models import Property

register = template.Library()


@typechecked
def property_filter(property, size: str):
    return '<i class="glyphicon glyphicon-tree-deciduous fa-{size}"></i>'.format(size=size)


@register.filter
@typechecked
def property_icon(property) -> str:
    return property_filter(property, 'lg')


@register.filter
@typechecked
def property_icon_hover(property) -> str:
    return property_filter(property, 'xl')


@register.filter
@typechecked
def property_status(status: Optional[str]) -> str:
    default = '#440bd4'

    if status is None:
        return default

    return {
        t[0]: t[1]
        for t in [
            (Property.Status.PENDING.value, '#f0ad4e'),
            (Property.Status.UNAUTHORIZED.value, '#c01c28'),
            (Property.Status.AUTHORIZED.value, '#440bd4'),
            (Property.Status.INACTIVE.value, '#666'),
        ]
    }.get(status, default)
