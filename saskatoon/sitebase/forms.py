from django.contrib.auth import forms as auth_forms
from django.utils.translation import gettext_lazy as _
from django.forms.widgets import PasswordInput
from member.models import AuthUser

class PasswordChangeForm(auth_forms.PasswordChangeForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        # replace widgets with placeholder values to fit Notika theme
        self.fields['old_password'].widget = PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password', 'placeholder': 'Old password', 'autofocus': True })
        self.fields['new_password1'].widget = PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'New password'})
        self.fields['new_password2'].widget = PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password', 'placeholder': 'Confirm password'})

    def save(self, commit=True):
        instance = super().save(commit)
        auth_user = AuthUser.objects.get(person=instance.person)
        auth_user.__setattr__('password_set', True)
        auth_user.save()
        return




