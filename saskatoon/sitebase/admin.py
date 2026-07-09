from django.contrib import admin, messages
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from logging import getLogger
from django.db.models import QuerySet
from typeguard import typechecked
from typing import Union

from sitebase.admin_filters import EmailIsDuplicateAdminFilter
from sitebase.models import Email, EmailContent, EmailType, FAQList, FAQItem, PageContent
from sitebase.serializers import EmailCommentSerializer, EmailRFPSerializer
from sitebase.tests import get_test_harvest
from sitebase.utils import maybe
from harvest.models import Comment, RequestForParticipation, Property
from member.models import Organization
from saskatoon.settings import SASKATOON_USER_AGENT

nominatim = Nominatim(user_agent=SASKATOON_USER_AGENT)
geocode = RateLimiter(nominatim.geocode, min_delay_seconds=1)
logger = getLogger('saskatoon')


@admin.action(description="Update map coordinates on selected entries")
@typechecked
def update_map_coordinates(modelAdmin, request, queryset: QuerySet[Union[Organization, Property]]):
    num_updated = 0
    num_errors = 0

    for entry in queryset:
        address = ' '.join(
            list(
                filter(
                    lambda a: a != '',
                    [
                        maybe(entry.street_number, ''),
                        maybe(entry.street, ''),
                        maybe(entry.city, '', lambda a: a.name),
                        maybe(entry.state, '', lambda a: a.name),
                        maybe(entry.postal_code, ''),
                        maybe(entry.country, '', lambda a: a.name),
                    ],
                )
            )
        )
        location = geocode(address)
        if location:
            entry.geom = {'type': 'Point', 'coordinates': [location.longitude, location.latitude]}
            entry.save()
            num_updated += 1
        else:
            num_errors += 1
            logger.error(
                f"Could not find coordinates for {entry.__class__.__name__} {entry.pk} at <{entry.short_address}>"
            )

    if num_errors > 0:
        messages.warning(
            request,
            f"{num_errors} addresses could not be found ({num_updated}/{num_updated + num_errors} coordinates successfully updated)",
        )
    else:
        messages.success(request, f"Successfully updated {num_updated} coordinates")


@admin.register(PageContent)
class ContentAdmin(admin.ModelAdmin[PageContent]):
    model = PageContent
    list_display = (
        'type',
        'title_en',
        'title_fr',
        'id',
    )


@admin.register(FAQItem)
class FAQuestionAdmin(admin.ModelAdmin[FAQItem]):
    model = FAQItem
    list_display = (
        'question_en',
        'question_fr',
        'id',
    )


@admin.register(FAQList)
class FAQAdmin(admin.ModelAdmin[FAQList]):
    model = FAQList
    list_display = (
        'name',
        'get_num_items',
        'is_active',
        'id',
    )

    @admin.display(description="Num. Items")
    def get_num_items(self, faq):
        return len(faq.items.all())


@admin.register(EmailContent)
class EmailContentAdmin(admin.ModelAdmin[EmailContent]):
    model = EmailContent
    list_display = (
        'type',
        'description',
        'id',
    )

    @admin.action(description="Test selected Email Content(s)")
    def test_email_content(self, request, queryset):
        recipient = request.user.person
        if recipient is None:
            return messages.error(request, f"User <{request.user}> has no Person attribute.")

        test_harvest = get_test_harvest()
        if test_harvest is None:
            return messages.error(request, "Could not retrieve test harvest.")

        test_data = {'password': 'abcdef123456'}
        test_data.update(EmailCommentSerializer(Comment.objects.last()).data)
        test_data.update(EmailRFPSerializer(RequestForParticipation.objects.last()).data)

        for email_content in queryset.exclude(type=EmailType.GENERIC_CLOSING):
            m = Email.objects.create(
                recipient=request.user.person,
                type=email_content.type,
                harvest=test_harvest,
            )
            if m.send(data=test_data):
                messages.success(
                    request,
                    f"<{email_content}> email successfully sent to {m.recipient.email}",
                )
            else:
                messages.error(
                    request,
                    f"Could not send <{email_content}> email to {m.recipient.email}",
                )

    actions = [
        test_email_content,
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin[Email]):
    model = Email
    list_display = (
        '__str__',
        'recipient',
        'type',
        'harvest',
        'sent',
        'date_sent',
        'id',
    )

    readonly_fields = list_display
    list_filter = ('type', 'sent', EmailIsDuplicateAdminFilter)

    @admin.action(description="Resend selected Email(s)")
    def resend_emails(self, request, queryset):
        for m in queryset.all():
            if m.resend():
                messages.success(
                    request,
                    f"<{m.type}> email successfully sent to {m.recipient.email}",
                )
            else:
                messages.error(
                    request,
                    f"Could not send <{m.type}> email to {m.recipient.email}",
                )

    actions = [resend_emails]
