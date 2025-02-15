from django.contrib import admin
from sitebase.models import Content, Email


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    model = Content
    list_display = (
        'type',
        'title_en',
        'title_fr',
        'id',
    )

    # def save_model(self, request, obj, form, change):
    #     """Make sure all_sent is False if users get added later on"""
    #     if obj.all_sent and obj.persons.filter(auth_user__password='').exists():
    #         obj.all_sent = False
    #         messages.add_message(
    #             request,
    #             messages.WARNING,
    #             f"Some users in {obj} were not yet invited."
    #         )
    #     super().save_model(request, obj, form, change)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    model = Email
    list_display = (
        'type',
        'description',
        'id',
    )
