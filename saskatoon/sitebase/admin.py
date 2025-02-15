from django.contrib import admin
from sitebase.models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    model = Content
    list_display = (
        'type',
        'title_en',
        'title_fr',
        'id',
    )
