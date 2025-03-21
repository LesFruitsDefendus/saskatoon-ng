from crequest.middleware import CrequestMiddleware
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, send_mass_mail
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from logging import getLogger

from saskatoon.settings import SEND_MAIL_FAIL_SILENTLY

logger = getLogger('saskatoon')


def clear_cache_property(sender, instance, **kwargs):
    cache.delete_pattern("*property*")


def clear_cache_harvest(sender, instance, **kwargs):
    cache.delete_pattern("*harvest*")


def clear_cache_organization(sender, instance, **kwargs):
    cache.delete_pattern("*organization*")


def clear_cache_equipment(sender, instance, **kwargs):
    cache.delete_pattern("*equipment*")


def clear_cache_people(sender, instance, **kwargs):
    cache.delete_pattern("*people*")


def _send_mail(subject, message, mail_to):
    subject = '[Saskatoon] ' + subject
    success = False
    try:
        num_sent = send_mail(
            subject,
            message,
            None,  # Using DEFAULT_FROM_EMAIL from settings.py
            mail_to,
            fail_silently=SEND_MAIL_FAIL_SILENTLY
        )
        success = num_sent > 0
    except Exception as e:
        logger.error("%s: %s", type(e), str(e))
    if success:
        logger.info("Successfully sent email <%s> to %s", subject, mail_to)
    else:
        logger.warning("Could not send email <%s> to %s", subject, mail_to)


def changed_by(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    if current_request:
        # If property is created by the owner not authenticated:
        if current_request.user.is_anonymous is False:
            instance.changed_by = current_request.user
    else:
        instance.changed_by = None


def notify_unselected_pickers(sender, instance, **kwargs):
    if instance.id:
        try:
            # this might raise DoesNotExist error while loading the fixtures
            # see https://github.com/LesFruitsDefendus/saskatoon-ng/issues/247
            # for more informations.
            original_instance = sender.objects.get(id=instance.id)
        except ObjectDoesNotExist:
            return
        if (original_instance.status is instance.Status.SCHEDULED and
                instance.status is instance.Status.READY):
            email_list = list()
            mail_subject = _("[Saskatoon] Request for participation declined")
            for picker in instance.get_unselected_pickers():
                message = (
                    _("Hi {},\n\n" +
                      "We are sorry but enough pickers have already been selected " +
                      "for the <{}> harvest. You may still be contacted by the pick-leader " +
                      "if some of them end up cancelling. We will do our " +
                      "best to prioritize your participation next time you submit a request " +
                      "re-using the same email for another harvest.\n\n" +
                      "Thanks for supporting your community!\n\n" +
                      "Yours,\n" +
                      "--\n" +
                      "Saskatoon Harvest System")
                ).format(picker.name, instance.get_public_title())
                email_list.append((mail_subject, message, None, [picker.email]))

            if email_list:
                harvest_str = f"<{instance} (id={instance.id})>"
                success = False
                try:
                    num_sent = send_mass_mail(email_list, fail_silently=SEND_MAIL_FAIL_SILENTLY)
                    success = num_sent == len(email_list)
                except Exception as e:
                    logger.error("%s: %s", type(e), str(e))
                if success:
                    logger.info(
                        "Successfully notified all unselected pickers about %s",
                        harvest_str
                    )
                else:
                    logger.warning(
                        "Could not notify some unselected pickers about %s",
                        harvest_str
                    )


def notify_pending_status_update(sender, instance, **kwargs):
    # Send email only if pending status is removed
    if instance.id:
        try:
            # this might raise DoesNotExist error while loading the fixtures
            # see https://github.com/LesFruitsDefendus/saskatoon-ng/issues/247
            # for more information.
            original_instance = sender.objects.get(id=instance.id)
        except ObjectDoesNotExist:
            return
        if original_instance.pending and not instance.pending:
            property_owner_email = list()
            if instance.owner:
                if not instance.owner.is_person and not instance.owner.is_organization:
                    logger.warning(
                        "Property owner (actor: %i) is not a Person nor an Organization.",
                        instance.owner.actor_id
                    )
                    return
                property_owner_name = instance.owner_name
                contact_email = instance.owner_email
            else:
                property_owner_name = instance.pending_contact_name
                contact_email = instance.pending_contact_email
            if not property_owner_name or not len(property_owner_name):
                logger.warning("Owner information missing for property %i", instance.id)
                return
            if not contact_email or not len(contact_email):
                logger.warning("Contact email missing for property %i:", instance.id)
                return
            property_owner_email.append(contact_email)
            mail_subject = _("Property Validation Completed")
            message = (
                _("Hi") + " " + property_owner_name + ",\n\n" +
                _("Your tree subscription has been validated by " +
                  "a member of Les Fruits Défendus. ") +
                _("A pick leader might contact you to plan a " +
                  "harvest this season.") + "\n\n" +
                _("Thanks for supporting your community!") + "\n\n" +
                _("Yours") + ",\n" +
                "--\n" +
                "Saskatoon Harvest System"
            )
            _send_mail(mail_subject, message, property_owner_email)


def comment_send_mail(sender, instance, **kwargs):
    # First check if pick_leader is set
    if instance.harvest.pick_leader:
        # Send email only if comment comes from someone else
        if instance.author.email != instance.harvest.pick_leader.email:
            # Building email content
            pick_leader_email = list()
            pick_leader_email.append(instance.harvest.pick_leader.email)
            pick_leader_name = instance.harvest.pick_leader.person.first_name
            mail_subject = u"New comment from %s" % instance.author
            message = u'Hi %s, \n\n' \
                      u'On %s %s left the following comment\n' \
                      u'in the harvest at "%s %s".\n\n' \
                      u'%s\n\n' \
                      u'You can see all information related to this ' \
                      u'harvest at\n' \
                      u'http://saskatoon.lesfruitsdefendus.org/harvest/%s.' \
                      u'\n\n' \
                      u'Yours,\n' \
                      u'--\n' \
                      u'Saskatoon Harvest System' % \
                      (
                          pick_leader_name,
                          instance.date_created.strftime('%b %d at %H:%M'),
                          instance.author,
                          instance.harvest.property.street_number,
                          instance.harvest.property.street,
                          instance.content,
                          instance.harvest.id
                      )

            # Sending email to pick leader
            _send_mail(mail_subject, message, pick_leader_email)


def rfp_send_mail(sender, instance, **kwargs):
    # First check if pick_leader is set
    if instance.harvest.pick_leader:
        # Send email only if request comes from someone else
        if instance.person.email != instance.harvest.pick_leader.email:
            # Building email content
            pick_leader_email = list()
            pick_leader_email.append(instance.harvest.pick_leader.email)
            pick_leader_name = instance.harvest.pick_leader.person.first_name
            mail_subject = u"New request for participation from %s" % instance.person
            message = u'Hi %s, \n\n' \
                      u'On %s %s requested to participate\n' \
                      u'in the harvest at "%s %s":\n\n' \
                      u'You can see all information related to this ' \
                      u'harvest at\n' \
                      u'http://saskatoon.lesfruitsdefendus.org/harvest/%s.' \
                      u'\n\n' \
                      u'Yours,\n' \
                      u'--\n' \
                      u'Saskatoon Harvest System' % \
                      (
                          pick_leader_name,
                          instance.date_created.strftime('%b %d at %H:%M'),
                          instance.person,
                          instance.harvest.property.street_number,
                          instance.harvest.property.street,
                          instance.harvest.id
                      )

            # Sending email to pick leader
            _send_mail(mail_subject, message, pick_leader_email)
