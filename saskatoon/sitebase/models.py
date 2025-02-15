from django.db import models
from django_quill.fields import QuillField
from django.utils.translation import gettext_lazy as _


class Content(models.Model):
    """Generic content model"""

    class Meta:
        verbose_name = _('Content')
        verbose_name_plural = _('Content')
        ordering = ['type']

    class Type(models.TextChoices):
        VOLUNTEER_HOME = 'volunteer_home', _("Volunteer Home")
        PICKLEADER_HOME = 'pickleader_home', _("Pickleader Home")
        TERMS_CONDITIONS = 'terms_conditions', _("Terms & Conditions")
        PRIVACY_POLICY = 'privacy_policy', _("Privacy Policy")

    type = models.CharField(
        verbose_name=_("Content type"),
        max_length=20,
        choices=Type.choices,
        null=True,
        blank=True,
        unique=True,
        default=None,
    )

    title_en = models.CharField(
        verbose_name="Title (en)",
        max_length=100,
        blank=True,
    )

    title_fr = models.CharField(
        verbose_name="Titre (fr)",
        max_length=100,
        blank=True,
    )

    subtitle_en = models.CharField(
        verbose_name="Subtitle (en)",
        max_length=100,
        blank=True,
    )

    subtitle_fr = models.CharField(
        verbose_name="Sous-titre (fr)",
        max_length=100,
        blank=True,
    )

    body_en = QuillField()

    body_fr = QuillField()

    def __str__(self):
        return "{}[{}]".format(self.type, self.id)

    def content(self, lang):
        return dict([(key, getattr(self, f"{key}_{lang}"))
                     for key in ['title', 'subtitle', 'body']])


class Email(models.Model):
    """Generic email model"""

    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')
        ordering = ['type']

    class Type(models.TextChoices):
        CLOSING = 'closing', _("Generic closing")  # -> generic
        NEW_RFP = 'new_rfp', _("New Request For Participation")  # -> Pickleader
        NEW_COMMENT = _("New Harvest Comment")   # -> Pickleader
        PROPERTY_VALIDATED = 'property_validated', _("Property was validated")  # -> Owner
        UNSELECTED_PICKERS = 'unselected_pickers', _("Unselected pickers")  # -> Volunteers
        SELECTED_PICKER = 'selected_picker', _("Selected picker")  # Volunteer

    type = models.CharField(
        verbose_name=_("Content type"),
        max_length=20,
        choices=Type.choices,
        null=True,
        blank=True,
        unique=True,
        default=None,
    )

    description = models.CharField(
        verbose_name=_("Ref. description"),
        max_length=100,
    )

    subject_en = models.CharField(
        verbose_name="Subject (en)",
        max_length=100,
        blank=True,
    )

    subject_fr = models.CharField(
        verbose_name="Objet (fr)",
        max_length=100,
        blank=True,
    )

    body_en = QuillField()

    body_fr = QuillField()

    def __str__(self):
        return "{}[{}]".format(self.type, self.id)

    def subject(self, lang):
        return "[Celtis] {}".format(
            getattr(self, f"subject_{lang}")
        )

    def body(self, lang):
        return getattr(self, f"body_{lang}")

    @staticmethod
    def closing(lang):
        o = Email.objects.filter(type='CLOSING').first()
        if o is None:
            raise Exception("Email closing not found.")

        return "{}\n\n{}".format(
            o.subject(lang),
            o.body(lang),
        )

    def content(self, lang):
        return "{}\n\n{}".format(
            self.body,
            self.closing(lang),
        )
