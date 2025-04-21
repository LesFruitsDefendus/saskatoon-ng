from django.contrib import admin, messages
from harvest.models import Harvest, Comment, RequestForParticipation
from sitebase.models import (
    Email,
    EmailContent,
    EmailType,
    PageContent
)
from sitebase.serializers import EmailCommentSerializer, EmailRFPSerializer


@admin.register(PageContent)
class ContentAdmin(admin.ModelAdmin):
    model = PageContent
    list_display = (
        'type',
        'title_en',
        'title_fr',
        'id',
    )


@admin.register(EmailContent)
class EmailContentAdmin(admin.ModelAdmin):
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
            messages.add_message(
                request,
                messages.ERROR,
                f"User <{request.user}> has no Person attribute."
            )
            return

        test_harvest = Harvest.objects.last()
        test_data = (
            dict(EmailCommentSerializer(Comment.objects.last()).data) |
            dict(EmailRFPSerializer(RequestForParticipation.objects.last()).data) |
            {'password': 'abcdef123456'}
        )

        for email_content in queryset.exclude(type=EmailType.GENERIC_CLOSING):
            m = Email.objects.create(
                recipient=request.user.person,
                type=email_content.type,
                harvest=test_harvest
            )
            if m.send(data=test_data) == 1:
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"<{email_content}> email successfully sent to {m.recipient.email}"
                )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"Could not send <{email_content}> email to {m.recipient.email}"
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
class EmailAdmin(admin.ModelAdmin):
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
