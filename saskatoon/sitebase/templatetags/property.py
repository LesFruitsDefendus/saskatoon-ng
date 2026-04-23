from django import template
from datetime import datetime
from typeguard import typechecked
from typing import Optional

from harvest.models import Property, Harvest

register = template.Library()


def harvests_for_year(harvests, year: int):
    return [h for h in harvests if datetime.strptime(h["start_date"], "%Y-%m-%d").year == year]


@typechecked
def property_filter(property, size: str, year: int):
    harvests = harvests_for_year(property["harvests"], year)

    if len(harvests) == 0:
        return '<i class="glyphicon glyphicon-home fa-{size}"></i>'.format(size=size)

    # Any upcoming harvests are more important then previously succeeded harvests
    prepared_harvest = [
        h
        for h in harvests
        if h["status"] in [Harvest.Status.ORPHAN, Harvest.Status.ADOPTED, Harvest.Status.SCHEDULED]
    ]

    if len(prepared_harvest) > 0:
        return '<i class="glyphicon glyphicon-tree-deciduous fa-{size}"></i>'.format(size=size)

    cancelled = [h for h in harvests if h["status"] in [Harvest.Status.CANCELLED]]

    if len(cancelled) > 0:
        '<i class="glyphicon glyphicon-apple fa-{size}"></i>'.format(size=size)

    success_or_ready = [
        h for h in harvests if h["status"] in [Harvest.Status.READY, Harvest.Status.SUCCEEDED]
    ]

    if len(success_or_ready) > 0:
        return '<i class="glyphicon glyphicon-apple fa-{size}"></i>'.format(size=size)

    return '<i class="glyphicon glyphicon-tree-deciduous fa-{size}"></i>'.format(size=size)


@register.filter
@typechecked
def property_icon(property, year: str) -> str:
    return property_filter(property, 'lg', int(year))


@register.filter
@typechecked
def property_icon_hover(property, year: str) -> str:
    return property_filter(property, 'xl', int(year))


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


@register.filter
@typechecked
def property_icon_color(property, year: str) -> str:
    harvests = harvests_for_year(property["harvests"], int(year))

    if (
        len(harvests) == 0
        or property["status"] != Property.Status.AUTHORIZED
        and datetime.now().year == int(year)
    ):
        return property_status(property["status"])

    # Any upcoming harvests are more important then previously succeeded harvests
    orphan_harvest = [h for h in harvests if h["status"] in [Harvest.Status.ORPHAN]]

    if len(orphan_harvest) > 0:
        return "#c01c28"

    adopted_harvest = [h for h in harvests if h["status"] == Harvest.Status.ADOPTED]

    if len(adopted_harvest) > 0:
        return "#000"

    scheduled_harvest = [h for h in harvests if h["status"] == Harvest.Status.SCHEDULED]

    if len(scheduled_harvest) > 0:
        return "#2da4f0"

    ready = [h for h in harvests if h["status"] == Harvest.Status.READY]

    if len(ready) > 0:
        return "#e8ad2b"

    cancelled_harvest = [h for h in harvests if h["status"] in [Harvest.Status.CANCELLED]]

    if len(cancelled_harvest) > 0:
        return "#c01c28"

    return "#440bd4"


@register.filter
@typechecked
def selected_season(request):
    if (
        'season' in request.GET
        and request.GET['season'] is not None
        and request.GET['season'] != ""
    ):
        return request.GET['season']

    return str(datetime.now().year)
