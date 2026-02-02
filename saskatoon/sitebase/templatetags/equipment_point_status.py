from django import template

register = template.Library()


@register.filter
def reservation(status: str) -> str:
    return {
        t[0]: t[1]
        for t in [
            ('reserved', '#c01c28'),
            ('available', '#007AFF'),
        ]
    }.get(status, '#000000')


def org_filter(org, size):
    if org['is_beneficiary'] and org['is_equipment_point']:
        return '<span class="fa-stack fa-{size}"><i class="fa-gift fa-solid"></i><i class="fa-scissors fa-solid"></i></span>'.format(
            size=size
        )

    if org['is_beneficiary']:
        return '<i class="fa-gift fa-solid fa-{size}"></i>'.format(size=size)

    if org['is_equipment_point']:
        return '<i class="fa-scissors fa-solid fa-{size}"></i>'.format(size=size)

    return '<i class="fa-location-pin fa-solid fa-{size}"></i>'.format(size=size)


@register.filter
def org_icon(org) -> str:
    return org_filter(org, 'xl')


@register.filter
def org_icon_hover(org) -> str:
    return org_filter(org, '2xl')
