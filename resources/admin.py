from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "resource_type",
        "source_name",
        "author",
        "published_at",
        "user",
        "created_at",
    )
    list_filter = ("resource_type", "source_name", "published_at", "created_at")
    search_fields = ("title", "source_name", "author", "url", "question", "answer", "user__email")
    readonly_fields = ("created_at", "updated_at")
