from crequest.middleware import CrequestMiddleware
from django.core.mail import send_mail
from django.core.cache import cache
from saskatoon.settings import SEND_MAIL_FAIL_SILENTLY
from django.utils.translation import gettext_lazy as _

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
    subject = '[Sakatoon] ' + subject
    send_mail(
            subject,
            message,
            None, # Using DEFAULT_FROM_EMAIL from settings.py
            mail_to,
            fail_silently=SEND_MAIL_FAIL_SILENTLY,
        )

def changed_by(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()
    if current_request:
        # If property is created by the owner not authenticated:
        if current_request.user.is_anonymous is False:
            instance.changed_by = current_request.user
    else:
        instance.changed_by = None

def notify_pending_status_update(sender, instance, **kwargs):
    # Send email only if pending status is removed
    if instance.id:
        original_instance = sender.objects.get(id=instance.id)
        if original_instance.pending and not instance.pending:
            property_owner_email = list()
            if instance.owner:
                    if not instance.owner.is_person and not instance.owner.is_organization:
                        # TODO: log this warning in a file
                        print(f"Property owner is neither a person nor an organization. " \
                             f"Unknown Actor: {instance.owner.actor_id}")
                        return
                    property_owner_name = instance.owner_name
                    contact_email = instance.owner_email
            else:
                property_owner_name = instance.pending_contact_name
                contact_email = instance.pending_contact_email
            if not property_owner_name or not len(property_owner_name):
                # TODO: log this warning in a file
                print("Property Owner information is missing")
                return
            if not contact_email or not len(contact_email):
                # TODO: log this warning in a file
                print("Property Owner contact email information is missing")
                return
            property_owner_email.append(contact_email)
            mail_subject = _("Property Validation Completed")
            message = (_("Hi") + " " + property_owner_name + ",\n\n" +
                    _("Your tree subscription has been validated by " +
                    "a member of Les Fruits Défendus. ") +
                    _("A pick leader might contact you to plan a " +
                    "harvest this season.") + "\n\n" +
                    _("Thanks for supporting your community!") + "\n\n" +
                    _("Yours") + ",\n" +
                    "--\n" +
                    "Saskatoon Harvest System")

            _send_mail(mail_subject, message, property_owner_email)

def comment_send_mail(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()

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
                      u'in the harvest at "%s %s":\n\n' \
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
                          instance.created_date.strftime('%b %d at %H:%M'),
                          instance.author,
                          instance.harvest.property.street_number,
                          instance.harvest.property.street,
                          instance.content,
                          instance.harvest.id
                      )

            # Sending email to pick leader
            _send_mail(mail_subject, message, pick_leader_email)

def rfp_send_mail(sender, instance, **kwargs):
    current_request = CrequestMiddleware.get_request()

    # First check if pick_leader is set
    if instance.harvest.pick_leader:
        # Send email only if request comes from someone else
        if instance.picker.email != instance.harvest.pick_leader.email:
            # Building email content
            pick_leader_email = list()
            pick_leader_email.append(instance.harvest.pick_leader.email)
            pick_leader_name = instance.harvest.pick_leader.person.first_name
            mail_subject = u"New request for participation from %s" % instance.picker
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
                          instance.creation_date.strftime('%b %d at %H:%M'),
                          instance.picker,
                          instance.harvest.property.street_number,
                          instance.harvest.property.street,
                          instance.harvest.id
                      )

            # Sending email to pick leader
            _send_mail(mail_subject, message, pick_leader_email)
