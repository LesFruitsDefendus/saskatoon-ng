# from django.core.validators import RegexValidator
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
        DRAFT = 'draft', _("Draft")
        VOLUNTEER_HOME = 'volunteer_home', _("Volunteer home page")
        PICKLEADER_HOME = 'pickleader_home', _("Pickleader home page")
        TERMS_CONDITIONS = 'terms_conditions', _("Terms & Conditions")
        PRIVACY_POLICY = 'privacy_policy', _("Privacy Policy")

    type = models.CharField(
        verbose_name=_("Reference name"),
        max_length=50,
        choices=Type.choices,
        default=Type.DRAFT,
        unique=True
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
        return "{}[{}]".format(self.name, self.id)

    def content(self, lang):
        return dict([(key, getattr(self, "{}_{}".format(key, lang)))
                     for key in ['title', 'subtitle', 'body']])
