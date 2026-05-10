from datetime import timedelta

from django.db.models import DateTimeField, Max
from django.db.models.functions import Coalesce, Greatest
from django.utils import timezone

from .models import JobApplication


def with_last_activity(queryset):
    return queryset.annotate(
        latest_contact_activity=Max("contacts__updated_at"),
        latest_note_activity=Max("notes__updated_at"),
    ).annotate(
        last_activity_at=Greatest(
            "updated_at",
            Coalesce(
                "latest_contact_activity",
                "updated_at",
                output_field=DateTimeField(),
            ),
            Coalesce(
                "latest_note_activity",
                "updated_at",
                output_field=DateTimeField(),
            ),
            output_field=DateTimeField(),
        )
    )


def archive_inactive_applications(user):
    auto_archive_days = user.profile.auto_archive_days or 30
    cutoff_date = timezone.now() - timedelta(days=auto_archive_days)

    active_applications = JobApplication.objects.filter(
        user=user,
        is_active=True,
        is_archived=False,
    )

    inactive_application_ids = list(
        with_last_activity(active_applications)
        .filter(last_activity_at__lte=cutoff_date)
        .values_list("id", flat=True)
    )

    if not inactive_application_ids:
        return 0

    return JobApplication.objects.filter(id__in=inactive_application_ids).update(
        is_archived=True,
        archived_at=timezone.now(),
    )


def touch_job_application(job_application):
    job_application.save(update_fields=["updated_at"])
