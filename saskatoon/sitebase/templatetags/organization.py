from django import template
from typeguard import typechecked
from typing import Optional

register = template.Library()


@register.filter
@typechecked
def reservation(status: Optional[str]) -> str:
    default = '#440bd4'

    if status is None:
        return default

    return {
        t[0]: t[1]
        for t in [
            ('reserved', '#c01c28'),
            ('available', '#440bd4'),
        ]
    }.get(status, default)


@typechecked
def org_filter(org, size: str):
    if org['is_beneficiary'] and org['is_equipment_point']:
        return '<span class="fa-stack fa-{size}"><i class="fa-gift fa-solid"></i><i class="fa-scissors fa-solid saskatoon-map-second-icon"></i></span>'.format(
            size=size
        )

    if org['is_beneficiary']:
        return '<i class="fa-gift fa-solid fa-{size}"></i>'.format(size=size)

    if org['is_equipment_point']:
        return '<i class="fa-scissors fa-solid fa-{size}"></i>'.format(size=size)

    return '<i class="fa-location-pin fa-solid fa-{size}"></i>'.format(size=size)


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
def org_active_tab(request) -> str:
    tab = request.GET.get('tab')

    return tab if tab == "map" else "table"
