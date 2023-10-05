# coding: utf-8
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
