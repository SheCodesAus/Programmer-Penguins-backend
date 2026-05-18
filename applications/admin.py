from django.contrib import admin
from .models import (
    ApplicationContact,
    ApplicationEvent,
    ApplicationNote,
    ApplicationTask,
    JobApplication,
)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "job_title",
        "company_name",
        "user",
        "status",
        "source_platform",
        "is_active",
        "is_archived",
        "created_at",
    )
    list_filter = ("status", "source_platform", "is_active", "is_archived", "created_at")
    search_fields = ("job_title", "company_name", "user__email", "job_url", "location")
    readonly_fields = ("created_at", "updated_at", "archived_at")


@admin.register(ApplicationContact)
class ApplicationContactAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "job_application",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "job_application__job_title",
        "job_application__company_name",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "job_application", "created_at", "updated_at")
    search_fields = ("title", "note", "job_application__job_title", "job_application__company_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ApplicationTask)
class ApplicationTaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "job_application",
        "task_type",
        "due_at",
        "completed_at",
        "auto_created",
        "is_required",
    )
    list_filter = ("task_type", "completed_at", "auto_created", "is_required")
    search_fields = ("title", "description", "job_application__job_title", "job_application__company_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ApplicationEvent)
class ApplicationEventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "job_application",
        "event_type",
        "starts_at",
        "ends_at",
        "location",
    )
    list_filter = ("event_type", "starts_at")
    search_fields = (
        "title",
        "location",
        "meeting_link",
        "contact_name",
        "contact_email",
        "job_application__job_title",
        "job_application__company_name",
    )
    readonly_fields = ("created_at", "updated_at")
