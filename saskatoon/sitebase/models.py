from django.db import models
from django.utils.translation import gettext_lazy as _

class Homepage(models.Model):

    pickleader_instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Pickleader Instructions in English"),
        help_text=_("Steps to pick a leader"),
        max_length=1000
    )

    date_created = models.DateTimeField(auto_now=True)
    
    class Meta:
        get_latest_by = 'date_created'