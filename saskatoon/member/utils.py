from django.core.mail import EmailMessage
from logging import getLogger
from member.models import AuthUser

logger = getLogger('saskatoon')


def send_reset_password_email(user: AuthUser, subject: str, message: str) -> bool:

    password = AuthUser.objects.make_random_password(16)
    user.set_password(password)
    user.__setattr__('password_set', False)
    user.save()

    mailto = user.email
    email = EmailMessage(subject, message.format(password=password), None, [mailto])

    try:
        email.send()
        logger.info("Successfully sent Reset Password email to %s", mailto)
        return True
    except Exception as e:
        logger.error("Failed sending Reset Password email to %s. %s: %s",
                     mailto, type(e), str(e))
        return False
