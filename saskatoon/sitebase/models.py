from django.core.mail import EmailMessage
from django.db import models
from django.dispatch import receiver
from django_quill.fields import QuillField
from django.utils import timezone as tz
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from logging import getLogger
from sortedm2m.fields import SortedManyToManyField
from typing import Dict, Any

from member.models import Person
from harvest.models import (
    Comment,
    Property,
    RequestForParticipation as RFP,
)
from sitebase.serializers import (
    EmailCommentSerializer,
    EmailHarvestSerializer,
    EmailPickLeaderSerializer,
    EmailPropertySerializer,
    EmailRFPSerializer,
    EmailRecipientSerializer,
)
from saskatoon.settings import (
    EMAIL_HOST,
    DEFAULT_FROM_EMAIL,
    DEFAULT_REPLY_TO_EMAIL,
)

logger = getLogger('saskatoon')


class PageContent(models.Model):
    """Generic content model"""

    class Meta:
        verbose_name = _('Page Content')
        verbose_name_plural = verbose_name
        ordering = ['type']

    class Type(models.TextChoices):
        VOLUNTEER_HOME = 'volunteer_home', _("Volunteer Home")
        PICKLEADER_HOME = 'pickleader_home', _("Pickleader Home")
        TERMS_CONDITIONS = 'terms_conditions', _("Terms & Conditions")
        PRIVACY_POLICY = 'privacy_policy', _("Privacy Policy")
        FAQ = 'faq', _("FAQ")

    type = models.CharField(
        verbose_name=_("Page type"),
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
        return dict(
            [(key, getattr(self, f"{key}_{lang}")) for key in ['title', 'subtitle', 'body']]
        )

    @staticmethod
    def get(type, lang):
        obj, _ = PageContent.objects.get_or_create(type=type)
        return obj.content(lang)


class FAQItem(models.Model):
    """Question / Answer"""

    class Meta:
        verbose_name = _("FAQ Item")
        verbose_name_plural = _("FAQ Items")
        ordering = ['id']

    question_en = models.CharField(
        verbose_name="Question (en)",
        max_length=255,
        blank=False,
    )

    question_fr = models.CharField(
        verbose_name="Question (fr)",
        max_length=255,
        blank=False,
    )

    answer_en = models.TextField(
        verbose_name="Answer (en)",
        blank=False,
    )

    answer_fr = models.TextField(
        verbose_name="Réponse (fr)",
        blank=False,
    )

    def dict(self, lang: str) -> dict[str, str]:
        return dict([(key, getattr(self, f"{key}_{lang}")) for key in ['question', 'answer']])

    def __str__(self):
        return "{}[{}]".format(self.question_en, self.id)


class FAQList(models.Model):
    """Frequently Asked Questions"""

    class Meta:
        verbose_name = _("FAQ List")
        verbose_name_plural = _("FAQ Lists")
        ordering = ['is_active', 'name']

    name = models.CharField(
        verbose_name=_("Ref. Name"),
        max_length=100,
        blank=False,
    )

    title_en = models.CharField(
        verbose_name="Title (en)",
        max_length=255,
        blank=False,
    )

    title_fr = models.CharField(
        verbose_name="Titre (fr)",
        max_length=255,
        blank=False,
    )

    items = SortedManyToManyField(FAQItem, verbose_name=_("Items"), sorted=True, blank=True)

    is_active = models.BooleanField(verbose_name=_("Enabled"), default=True, null=False)

    def __str__(self):
        return "{}[{}]".format(self.name, self.id)


class EmailType(models.TextChoices):
    GENERIC_CLOSING = 'closing', _("Closing (common)")

    # PickLeader
    REGISTRATION = 'registration', _("Pickleader Registration Invite")
    PASSWORD_RESET = 'password_reset', _("Password Reset")
    NEW_HARVEST_RFP = 'new_rfp', _("New Request For Participation")
    NEW_HARVEST_COMMENT = 'new_comment', _("New Harvest Comment")

    # Owner
    PROPERTY_REGISTERED = 'property_registered', _("Property was registered")
    SEASON_AUTHORIZATION = 'season_authorization', _("Seasonal property authorization")

    # Volunteers
    UNSELECTED_PICKERS = 'unselected_pickers', _("Unselected pickers")
    SELECTED_PICKER = 'selected_picker', _("Selected picker")
    REJECTED_PICKER = 'rejected_picker', _("Rejected picker")


class EmailContent(models.Model):
    """Generic email content model"""

    class Meta:
        verbose_name = _('Email Content')
        verbose_name_plural = verbose_name
        ordering = ['id']

    type = models.CharField(
        verbose_name=_("Email type"),
        max_length=20,
        choices=EmailType.choices,
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
    )

    subject_fr = models.CharField(
        verbose_name="Objet (fr)",
        max_length=100,
    )

    body_en = models.TextField(
        verbose_name=_("Body (en)"),
    )

    body_fr = models.TextField(
        verbose_name=_("Corps (fr)"),
    )

    def __str__(self):
        return self.type

    def subject(self, lang):
        return "[Les Fruits Défendus] {}".format(getattr(self, f"subject_{lang}"))

    def body(self, lang):
        return getattr(self, f"body_{lang}")

    def message(self, lang):
        return "{}\n\n\n{}".format(
            self.body(lang),
            self.closing(lang),
        )

    @staticmethod
    def closing(lang):
        return EmailContent.get(EmailType.GENERIC_CLOSING).body(lang)

    @staticmethod
    def get(type):
        obj, _ = EmailContent.objects.get_or_create(type=type)
        return obj


class Email(models.Model):
    """Email model"""

    class Meta:
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")

    recipient = models.ForeignKey(
        'member.Person',
        related_name='emails',
        verbose_name=_("Recipient"),
        on_delete=models.CASCADE,
    )

    type = models.CharField(
        verbose_name=_("Email type"),
        max_length=20,
        choices=EmailType.choices,
    )

    harvest = models.ForeignKey(
        'harvest.Harvest',
        verbose_name=_("Harvest"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    sent = models.BooleanField(verbose_name=_("Successfully sent"), default=False)

    body = models.TextField(
        blank=True,
    )

    log = models.TextField(
        blank=True,
    )

    date_sent = models.DateTimeField(
        verbose_name=_("Date"),
        blank=True,
        null=True,
    )

    def __str__(self):
        return "<{type}> {mailto}".format(type=self.type, mailto=self.recipient.email)

    @property
    def content(self):
        return EmailContent.get(self.type)

    @property
    def harvest_data(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if self.harvest is not None:
            data.update(EmailHarvestSerializer(self.harvest).data)
            data.update(EmailPickLeaderSerializer(self.harvest.pick_leader).data)
            data.update(EmailPropertySerializer(self.harvest.property).data)

        return data

    @property
    def recipient_data(self) -> Dict[str, Any]:
        return dict(EmailRecipientSerializer(self.recipient).data)

    @property
    def cc_list(self):
        if self.harvest is None or self.harvest.pick_leader is None:
            return []
        return [self.harvest.pick_leader.email]

    @property
    def bcc_list(self):
        return [DEFAULT_FROM_EMAIL]

    @property
    def reply_to_list(self):
        if self.harvest is None:
            return [DEFAULT_REPLY_TO_EMAIL]
        return [self.harvest.pick_leader.email]

    def get_subject(self, data: Dict[str, str]) -> str:
        subject = self.content.subject(self.recipient.language)
        return subject.format(**data)

    def get_intro(self, lang):
        return {
            'fr': f"Bonjour {self.recipient.name},\n\n",
            'en': f"Hi {self.recipient.name},\n\n",
        }[lang]

    def get_default_message(self, data: Dict[str, str]) -> str:
        if self.recipient.language == Person.Language.FR:
            msg = "* * English version follows * *\n\n{fr}\n\n{sep}\n\n{en}"
        else:
            msg = "* * Version française plus bas * *\n\n{en}\n\n{sep}\n\n{fr}"

        msg = msg.format(
            fr=self.get_intro('fr') + self.content.message('fr'),
            en=self.get_intro('en') + self.content.message('en'),
            sep="___________________________________",
        )

        return msg.format(**data)

    def record_sent(self, success: bool, body: str, log: str) -> bool:
        self.date_sent = tz.now()
        self.sent = success
        self.body = body
        self.log += log
        self.save()
        return success

    def record_success(self, body: str) -> bool:
        log = f"Successfully sent email {self}."
        logger.info(log)
        return self.record_sent(True, body, log)

    def record_failure(self, body: str, error_msg: str) -> bool:
        log = f"Could not send email {self}. {error_msg}."
        logger.error(log)
        return self.record_sent(False, body, log)

    def send(self, message=None, data: Dict[str, str] = {}) -> bool:
        if self.recipient.email is None:
            return self.record_failure(message, "Person <self.recipient> has no email address.")

        data.update(self.harvest_data)
        data.update(self.recipient_data)

        if message is None:
            message = self.get_default_message(data)

        if not EMAIL_HOST:
            return self.record_failure(message, "SMTP server not configured")

        m = EmailMessage(
            subject=self.get_subject(data),
            body=message,
            from_email=DEFAULT_FROM_EMAIL,
            to=[self.recipient.email],
            cc=self.cc_list,
            bcc=self.bcc_list,
            reply_to=self.reply_to_list,
        )

        try:
            if m.send() == 1:
                return self.record_success(message)
        except Exception as e:
            return self.record_failure(message, f"{type(e)}: {str(e)}")

        return self.record_failure(message, "Something went wrong.")


@receiver(pre_save, sender=Property)
def notify_property_validated(sender, instance, **kwargs):
    if not instance.id or instance.pending:
        return

    try:
        original = sender.objects.get(id=instance.id)
        if not original.pending:
            return
    except Property.DoesNotExist:
        pass

    return notify_property_registered(sender, instance, **kwargs)


@receiver(post_save, sender=Property)
def notify_property_created(sender, instance, created, **kwargs):
    if not created or instance.pending:
        return

    return notify_property_registered(sender, instance, **kwargs)


def notify_property_registered(_sender, instance, **kwargs):
    if instance.owner is None:
        logger.warning("Property %i has no registered owner.", instance.id)
        return

    recipient = instance.email_recipient
    if recipient is None:
        logger.warning(
            "Property owner (actor: %i) is not a Person nor an Organization.",
            instance.owner.actor_id,
        )
        return

    Email.objects.create(
        recipient=recipient,
        type=EmailType.PROPERTY_REGISTERED,
    ).send(data=dict(EmailPropertySerializer(instance).data))


"""disabled
@receiver(pre_save, sender=Harvest)
def notify_unselected_pickers(sender, instance, **kwargs):
    try:
        original = sender.objects.get(id=instance.id)
        if original.status != Harvest.Status.SCHEDULED:
            return
    except Harvest.DoesNotExist:
        pass

    if instance.status == Harvest.Status.READY:
        for r in instance.requests.filter(status=RFP.Status.PENDING):
            if Email.objects.create(
                recipient=r.person,
                type=EmailType.UNSELECTED_PICKERS,
                harvest=instance,
            ).send():
                r.status = RFP.Status.DECLINED
                r.save()
"""


@receiver(post_save, sender=RFP)
def notify_new_request_for_participation(sender, instance, created, **kwargs):
    if created:
        pick_leader = instance.harvest.pick_leader
        if pick_leader is None or pick_leader is instance.person:
            return

        Email.objects.create(
            recipient=pick_leader.person,
            type=EmailType.NEW_HARVEST_RFP,
            harvest=instance.harvest,
        ).send(data=dict(EmailRFPSerializer(instance).data))


@receiver(post_save, sender=Comment)
def notify_new_harvest_comment(sender, instance, **kwargs):
    pick_leader = instance.harvest.pick_leader
    if pick_leader is None or pick_leader is instance.author:
        return

    Email.objects.create(
        recipient=pick_leader.person,
        type=EmailType.NEW_HARVEST_COMMENT,
        harvest=instance.harvest,
    ).send(data=dict(EmailCommentSerializer(instance).data))
