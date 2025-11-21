from django.contrib import admin, messages
from harvest.models import Comment, RequestForParticipation
from sitebase.models import Email, EmailContent, EmailType, PageContent
from sitebase.serializers import EmailCommentSerializer, EmailRFPSerializer
from sitebase.tests import get_test_harvest


@admin.register(PageContent)
class ContentAdmin(admin.ModelAdmin[PageContent]):
    model = PageContent
    list_display = (
        'type',
        'title_en',
        'title_fr',
        'id',
    )


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
            if m.send(data=test_data) == 1:
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
    list_filter = ('type', 'sent')
