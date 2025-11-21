from django import template
from typing import Optional

from harvest.models import Harvest
from member.models import AuthUser
import member.permissions as perms

register = template.Library()


@register.filter
def is_person(actor):
    return actor.is_person


@register.filter(name="is_core_or_admin")
def is_core_or_admin(user: AuthUser) -> bool:
    """checks if the user making the request has the groups core or admin"""

    return perms.is_core_or_admin(user)


@register.filter(name="is_pickleader")
def is_pickleader(user: AuthUser, hid: Optional[int] = None) -> bool:
    """checks if the user making the request is a or *the* pickleader"""

    if hid is not None:
        harvest = Harvest.objects.get(id=hid)
        return harvest.pick_leader == user

    return perms.is_pickleader_or_core(user)


@register.filter(name="is_translator")
def is_translator(user: AuthUser) -> bool:
    """checks if the user making the request can access Rosetta"""

    return perms.is_translator(user)
