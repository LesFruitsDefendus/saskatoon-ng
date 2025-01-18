from django.core.mail import EmailMessage
from logging import getLogger
from member.models import AuthUser
from secrets import choice
from typing import Optional

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
