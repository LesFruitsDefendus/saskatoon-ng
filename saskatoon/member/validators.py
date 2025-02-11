from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from member.models import AuthUser


def validate_email(email, auth_user=None):
    '''Check if a user with same email address is already registered'''

    if email:
        duplicates = AuthUser.objects.filter(email=email)
        if auth_user:
            duplicates = duplicates.exclude(id=auth_user.id)
        if duplicates.exists():
            raise ValidationError(
                _("Email address < {} > is already registered!").format(email)
            )
    elif auth_user:
        raise ValidationError(_("Please enter an email address."))


def validate_new_password(old_password, new_password):
    """
    Validate that the new_password does not match old_password.
    """
    if new_password is not None and old_password == new_password:
        raise ValidationError(
            _("Your new password must be different than your old password.")
        )
    return new_password
