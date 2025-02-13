from django import template
from member.models import AuthUser

register = template.Library()


@register.filter
def is_person(actor):
    return actor.is_person


@register.filter(name="is_core_or_admin")
def is_core_or_admin(user: AuthUser) -> bool:
    """checks if the user making the request has the groups core or admin"""

    return user.groups.filter(name__in=("admin", "core")).exists()
