from django.contrib import admin
from .models import FeedbackMessage


@admin.register(FeedbackMessage)
class FeedbackMessageAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "message_type",
        "related_page",
        "subject",
        "consent_given",
        "created_at",
    )
    list_filter = ("message_type", "related_page", "consent_given", "created_at")
    search_fields = ("email", "first_name", "last_name", "subject", "message")
    readonly_fields = ("created_at",)
