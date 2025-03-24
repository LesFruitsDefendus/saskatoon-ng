from crequest.middleware import CrequestMiddleware
from django.core.cache import cache
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from logging import getLogger

from member.models import (
    Organization,
    Person,
)
from harvest.models import (
    Comment,
    Equipment,
    Harvest,
    Property,
    RequestForParticipation,
)
from sitebase.models import Email, EmailContent
from sitebase.serializers import EmailCommentSerializer, EmailPropertySerializer

logger = getLogger('saskatoon')


@receiver(post_save, sender=Property)
def clear_cache_property(sender, instance, **kwargs):
    cache.delete_pattern("*property*")


@receiver(post_save, sender=Harvest)
def clear_cache_harvest(sender, instance, **kwargs):
    cache.delete_pattern("*harvest*")


@receiver(post_save, sender=Organization)
def clear_cache_organization(sender, instance, **kwargs):
    cache.delete_pattern("*organization*")


@receiver(post_save, sender=Equipment)
def clear_cache_equipment(sender, instance, **kwargs):
    cache.delete_pattern("*equipment*")


@receiver(post_save, sender=Person)
def clear_cache_people(sender, instance, **kwargs):
    cache.delete_pattern("*person*")


@receiver(pre_save, senser=Harvest)
def harvest_changed_by(sender, instance, **kwargs):
    request = CrequestMiddleware.get_request()
    if not request:
        return
    instance.changed_by = \
        None if request.user.is_anonymous else request.user


@receiver(pre_save, sender=Harvest)
def notify_unselected_pickers(sender, instance, **kwargs):
    if instance.id:
        original = sender.objects.get(id=instance.id)

        if instance.status == Harvest.Status.READY and \
           original.status == Harvest.Status.SCHEDULED:
            for picker in instance.get_unselected_pickers():
                Email.objects.create(
                    recipient=picker,
                    type=EmailContent.Type.UNSELECTED_PICKERS,
                    harvest=instance,
                ).send()


@receiver(pre_save, sender=Property)
def notify_property_registered(sender, instance, **kwargs):
    if instance.id and instance.owner is not None:
        original = sender.objects.get(id=instance.id)

        if original.pending and not instance.pending:
            if instance.owner.is_person:
                recipient = instance.owner
            elif instance.owner.is_organization:
                recipient = instance.owner.contact_person
            else:
                logger.warning(
                    "Property owner (actor: %i) is not a Person nor an Organization.",
                    instance.owner.actor_id
                )
                return

            Email.objects.create(
                recipient=recipient,
                type=EmailContent.Type.PROPERTY_REGISTERED,
            ).send(data=EmailPropertySerializer(instance).data)


@receiver(post_save, sender=Comment)
def notify_new_harvest_comment(sender, instance, **kwargs):
    pick_leader = instance.harvest.pick_leader
    if pick_leader is None or pick_leader is instance.author:
        return

    Email.objects.create(
        recipient=pick_leader,
        type=EmailContent.Type.NEW_HARVEST_COMMENT,
        harvest=instance.harvest,
    ).send(data=EmailCommentSerializer(instance).data)


@receiver(post_save, sender=RequestForParticipation)
def notify_new_request_for_participation(sender, instance, **kwargs):
    pick_leader = instance.harvest.pick_leader
    if pick_leader is None or pick_leader is instance.picker:
        return

    Email.objects.create(
        recipient=pick_leader,
        type=EmailContent.Type.NEW_HARVEST_RFP,
        harvest=instance.harvest,
    ).send()
