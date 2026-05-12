from django import template
from datetime import datetime
from typeguard import typechecked
from typing import Optional

from harvest.models import Property, Harvest
from sitebase.templatetags.harvest_status import color, harvest_filter

register = template.Library()


@typechecked
def harvests_for_year(harvests, year: int):
    return [h for h in harvests if datetime.strptime(h["start_date"], "%Y-%m-%d").year == year]


@register.filter
@typechecked
def property_icon_shape(size: str) -> str:
    return '<i class="glyphicon glyphicon-home fa-{size}"></i>'.format(size=size)


@typechecked
def show_property(harvests, status: Property.Status, year: int) -> bool:
    return (
        len(harvests) == 0 or status != Property.Status.AUTHORIZED and datetime.now().year == year
    )


@typechecked
def property_filter(property, size: str, year: int) -> str:
    harvests = harvests_for_year(property['harvests'], year)

    if show_property(harvests, property['status'], year):
        return property_icon_shape(size)

    if property['next_harvest']:
        return harvest_filter(property['next_harvest']['status'], size)

    if property['last_succeeded_harvest']:
        return harvest_filter(property['last_succeeded_harvest']['status'], size)

    cancelled_harvest = [h for h in harvests if h["status"] in [Harvest.Status.CANCELLED]]

    if len(cancelled_harvest) > 0:
        return color(Harvest.Status.CANCELLED)

    return '<i class="glyphicon glyphicon-tree-deciduous fa-{size}"></i>'.format(size=size)


@register.filter
@typechecked
def property_icon(property, year_str: str) -> str:
    return property_filter(property, 'lg', int(year_str))


@register.filter
@typechecked
def property_icon_hover(property, year_str: str) -> str:
    return property_filter(property, 'xl', int(year_str))


@register.filter
@typechecked
def property_status(status: Optional[str]) -> str:
    default = 'saskatoon-primary'

    if status is None:
        return default

    return {
        t[0]: t[1]
        for t in [
            (Property.Status.PENDING.value, 'saskatoon-warning'),
            (Property.Status.UNAUTHORIZED.value, 'saskatoon-danger'),
            (Property.Status.AUTHORIZED.value, 'saskatoon-success'),
            (Property.Status.INACTIVE.value, 'saskatoon-neutral'),
        ]
    }.get(status, default)


@register.filter
@typechecked
def property_icon_color(property, year_str: str) -> str:
    year = int(year_str)
    harvests = harvests_for_year(property['harvests'], year)

    if show_property(harvests, property['status'], year):
        return property_status(property['status'])

    if property['next_harvest']:
        return color(property['next_harvest']['status'])

    if property['last_succeeded_harvest']:
        return color(property['last_succeeded_harvest']['status'])

    cancelled_harvest = [h for h in harvests if h["status"] in [Harvest.Status.CANCELLED]]

    if len(cancelled_harvest) > 0:
        return color(Harvest.Status.CANCELLED)

    return "saskatoon-success"


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
