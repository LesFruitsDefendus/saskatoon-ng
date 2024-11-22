from datetime import datetime
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from logging import getLogger
from member.models import AuthUser, Organization
from secrets import choice
from typing import Optional

from harvest.models import Harvest, Equipment

logger = getLogger('saskatoon')


def make_random_password(length=10) -> str:
    allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return ''.join(choice(allowed_chars) for i in range(length))


def reset_password(user: AuthUser) -> str:
    password = make_random_password(12)
    user.set_password(password)
    user.has_temporary_password = True
    user.save()
    return password


def send_reset_password_email(user: AuthUser, subject: str, message: str) -> bool:
    email = EmailMessage(
        subject,
        message.format(password=reset_password(user)),
        None,
        [user.email]
    )
    try:
        email.send()
        logger.info("Successfully sent Reset Password email to %s", user.email)
        return True
    except Exception as e:
        logger.error("Failed sending Reset Password email to %s. %s: %s",
                     user.email, type(e), str(e))
        return False


def send_invite_email(user: AuthUser, subject: str, message: str) -> Optional[str]:
    email = EmailMessage(
        subject,
        message.format(password=reset_password(user)),
        None,
        [user.email]
    )
    try:
        email.send()
        logger.info("Successfully sent Invitation email to %s", user.email)
        return None
    except Exception as e:
        user.password = ''
        user.has_temporary_password = False
        user.save()
        error_msg = f"{type(e)}: {str(e)}"
        logger.error("Failed sending Invitation email to %s. %s", user.email, error_msg)
        return error_msg

def get_equipment_points_available_in_daterange(start_date: datetime, end_date: datetime):
    """"
    Returns equipment points where the given start and end date range does not conflict with
    the start and end date ranges of other harvests that
    have already reserved equipment owned by this equipment_point.
    """

    # 1. get all harvests that conflict with date range
    q0 = Q(start_date__range=(start_date, end_date))
    q1 = Q(end_date__range=(start_date, end_date))
    q2 = Q(start_date__gt=start_date)
    q3 = Q(end_date__gt=start_date)
    q4 = Q(start_date__lt=end_date)
    q5 = Q(end_date__lt=end_date)
    conflicting_harvests = Harvest.objects.all().filter(q0 | q1 | (q2 and q3) | (q4 and q5))

    # 2. get all equipment reserved by those harvests
    conflicting_reserved_equipment = Equipment.objects.all().filter(id__in=conflicting_harvests.values_list("equipment_reserved", flat=True))

    # 3. find owners of reserved equipment
    conflicting_equipment_points = conflicting_reserved_equipment.values_list("owner", flat=True).distinct()
    available_equipment_points = Organization.objects.all().exclude(actor_id__in=conflicting_equipment_points)

    return available_equipment_points

