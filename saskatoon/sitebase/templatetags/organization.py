from django import template
from typeguard import typechecked
from typing import Optional

from sitebase.templatetags.harvest_status import make_icon

register = template.Library()


@register.filter
@typechecked
def reservation(status: Optional[str]) -> str:
    default = 'saskatoon-primary'

    if status is None:
        return default

    return {
        t[0]: t[1]
        for t in [
            ('reserved', 'saskatoon-danger'),
            ('available', 'saskatoon-success'),
        ]
    }.get(status, default)


@register.filter
@typechecked
def equipment_point_icon_shape(size: str) -> str:
    return '<i class="fa-scissors fa-solid fa-{size}"></i>'.format(size=size)


@register.filter
@typechecked
def beneficiary_icon_shape(size: str) -> str:
    return '<i class="fa-gift fa-solid fa-{size}"></i>'.format(size=size)


@register.filter
@typechecked
def default_icon_shape(size: str) -> str:
    return '<i class="fa-location-pin fa-solid fa-{size}"></i>'.format(size=size)


@typechecked
def org_filter(org, size: str, mode: str) -> str:
    if org['is_equipment_point']:
        return make_icon(equipment_point_icon_shape, size, mode)

    if org['is_beneficiary']:
        return make_icon(beneficiary_icon_shape, size, mode)

    return make_icon(default_icon_shape, size, mode)


@register.filter
@typechecked
def org_icon(org) -> str:
    return org_filter(org, 'lg')


@register.filter
@typechecked
def org_icon_hover(org) -> str:
    return org_filter(org, 'xl')


@register.filter
@typechecked
def org_icon_stacked(org) -> str:
    return org_filter(org, 'lg', 'stack')


@register.filter
@typechecked
def org_icon_stacked_hover(org) -> str:
    return org_filter(org, 'xl', 'stack')


@register.filter
@typechecked
def org_active_tab(request) -> str:
    tab = request.GET.get('tab')

    return tab if tab == "map" else "table"
