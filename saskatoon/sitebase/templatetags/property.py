from django import template
from django.utils.translation import gettext_lazy as _
from typeguard import typechecked
from typing import Optional

from harvest.models import Property, Harvest
from sitebase.templatetags.harvest_status import (
    color,
    harvest_filter,
    upcoming_harvests,
    make_icon,
    tree_icon,
)

register = template.Library()


@register.filter
@typechecked
def property_icon_shape(size: str) -> str:
    return '<i class="glyphicon glyphicon-home fa-{size}"></i>'.format(size=size)


@typechecked
def show_property(harvests, status: Property.Status) -> bool:
    return len(harvests) == 0 or status != Property.Status.AUTHORIZED


@typechecked
def property_filter(property, size: str, mode: str = 'flat') -> str:
    if show_property(property['harvests'], property['status']):
        return make_icon(property_icon_shape, size, mode)

    next = upcoming_harvests(property['harvests'])
    if len(next) > 0:
        return harvest_filter(next[0]['status'], size, mode)

    if property['last_succeeded_harvest']:
        return harvest_filter(property['last_succeeded_harvest']['status'], size, mode)

    cancelled_harvest = [
        h for h in property['harvests'] if h["status"] in [Harvest.Status.CANCELLED]
    ]

    if len(cancelled_harvest) > 0:
        return harvest_filter(Harvest.Status.CANCELLED, size, mode)

    return make_icon(tree_icon, size, mode)


@register.filter
@typechecked
def harvest_details_icon(status, size: str) -> str:
    return harvest_filter(status, size)


@register.filter
@typechecked
def harvest_details_icon_stacked(status, size: str) -> str:
    return harvest_filter(status, size, 'stack')


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
def property_icon_stacked(property) -> str:
    return property_filter(property, 'lg', 'stack')


@register.filter
@typechecked
def property_icon_stacked_hover(property) -> str:
    return property_filter(property, 'xl', 'stack')


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
            (Property.Status.VALIDATED.value, 'saskatoon-info'),
        ]
    }.get(status, default)


@register.filter
@typechecked
def property_icon_color(property) -> str:
    if show_property(property['harvests'], property['status']):
        return property_status(property['status'])

    next = upcoming_harvests(property['harvests'])
    if len(next) > 0:
        return color(next[0]['status'])

    if property['last_succeeded_harvest']:
        return color(property['last_succeeded_harvest']['status'])

    cancelled_harvest = [
        h for h in property['harvests'] if h["status"] in [Harvest.Status.CANCELLED]
    ]

    if len(cancelled_harvest) > 0:
        return color(Harvest.Status.CANCELLED)

    return "saskatoon-success"


@register.filter
@typechecked
def harvest_details_color(status) -> str:
    return color(status)


@register.filter
@typechecked
def property_status_attributes(status):
    default = ''

    if status is None:
        return default

    help_text = {
        t[0]: t[1]
        for t in [
            (
                Property.Status.PENDING.value,
                _("The property information needs to be validated by a core member."),
            ),
            (
                Property.Status.UNAUTHORIZED.value,
                _(
                    "The property owner does not want a harvest this season, please don't contact them"
                ),
            ),
            (
                Property.Status.AUTHORIZED.value,
                _("If this property does not already have a harvest, you can create one"),
            ),
            (Property.Status.INACTIVE.value, _("This property is inactive")),
            (
                Property.Status.VALIDATED.value,
                _(
                    "The property owner has not yet indicated whether they want to participate this year, you may contact them to confirm"
                ),
            ),
        ]
    }.get(status, default)

    return 'data-placement="bottom" data-toggle="tooltip" title="' + help_text + '"'
