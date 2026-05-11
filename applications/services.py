from datetime import timedelta

from django.db import IntegrityError
from django.db.models import DateTimeField, Max
from django.db.models.functions import Coalesce, Greatest
from django.utils import timezone

from .models import ApplicationEvent, ApplicationTask, JobApplication


FOUND_TASKS = [
    {
        "task_type": ApplicationTask.TaskType.TAILOR_RESUME,
        "title": "Tailor resume for this role",
        "description": "Adjust your resume so the most relevant experience and skills match this vacancy.",
        "is_required": True,
    },
    {
        "task_type": ApplicationTask.TaskType.COVER_LETTER,
        "title": "Prepare cover letter",
        "description": "Write a short cover letter if the vacancy asks for one or if it would strengthen your application.",
        "is_required": False,
    },
    {
        "task_type": ApplicationTask.TaskType.SUBMIT_APPLICATION,
        "title": "Submit application",
        "description": "Send the application. Completing this task moves the card to Applied.",
        "is_required": True,
        "triggers_status_change_to": JobApplication.Status.APPLIED,
    },
]


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


def add_business_days(start_at, days):
    current = start_at
    added_days = 0

    while added_days < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added_days += 1

    return current


def create_auto_task(application, task_type, defaults):
    try:
        task, _ = ApplicationTask.objects.get_or_create(
            job_application=application,
            task_type=task_type,
            auto_created=True,
            defaults=defaults,
        )
        return task
    except IntegrityError:
        return ApplicationTask.objects.filter(
            job_application=application,
            task_type=task_type,
            auto_created=True,
        ).first()


def ensure_found_application_tasks(application):
    if application.status != JobApplication.Status.FOUND:
        return

    for task in FOUND_TASKS:
        defaults = {
            "title": task["title"],
            "description": task["description"],
            "source_status": JobApplication.Status.FOUND,
            "is_required": task.get("is_required", True),
            "triggers_status_change_to": task.get("triggers_status_change_to", ""),
        }

        create_auto_task(application, task["task_type"], defaults)


def ensure_applied_follow_up_task(application):
    if application.status != JobApplication.Status.APPLIED:
        return

    create_auto_task(
        application,
        ApplicationTask.TaskType.FOLLOW_UP,
        {
            "title": "Follow up with the company",
            "description": "If you have not heard back, find a relevant HR/contact person and let them know you applied.",
            "source_status": JobApplication.Status.APPLIED,
            "due_at": add_business_days(timezone.now(), 5),
            "is_required": False,
        },
    )


def ensure_interviewing_tasks(application):
    if application.status != JobApplication.Status.INTERVIEWING:
        return

    create_auto_task(
        application,
        ApplicationTask.TaskType.INTERVIEW_PREP,
        {
            "title": "Prepare for the interview",
            "description": "Review the role, prepare examples, questions, and logistics before the interview.",
            "source_status": JobApplication.Status.INTERVIEWING,
            "is_required": False,
        },
    )


def ensure_rejection_feedback_task(application):
    if application.status != JobApplication.Status.REJECTED:
        return

    create_auto_task(
        application,
        ApplicationTask.TaskType.REJECTION_FEEDBACK,
        {
            "title": "Thank them and ask for feedback",
            "description": "Send a polite thank-you note and ask whether they can share feedback for future applications.",
            "source_status": JobApplication.Status.REJECTED,
            "is_required": False,
        },
    )


def ensure_offer_review_task(application):
    if application.status != JobApplication.Status.OFFER:
        return

    create_auto_task(
        application,
        ApplicationTask.TaskType.OFFER_REVIEW,
        {
            "title": "Review offer details",
            "description": "Check salary, benefits, start date, response deadline, and questions before accepting.",
            "source_status": JobApplication.Status.OFFER,
            "is_required": True,
        },
    )


def ensure_status_tasks(application):
    ensure_found_application_tasks(application)
    ensure_applied_follow_up_task(application)
    ensure_interviewing_tasks(application)
    ensure_rejection_feedback_task(application)
    ensure_offer_review_task(application)


def complete_application_task(task):
    if not task.completed_at:
        task.completed_at = timezone.now()
        task.save(update_fields=["completed_at", "updated_at"])

    application = task.job_application

    if (
        task.triggers_status_change_to
        and application.status != task.triggers_status_change_to
    ):
        application.status = task.triggers_status_change_to

        update_fields = ["status", "updated_at"]

        if (
            task.triggers_status_change_to == JobApplication.Status.APPLIED
            and not application.date_applied
        ):
            application.date_applied = timezone.localdate()
            update_fields.append("date_applied")

        application.save(update_fields=update_fields)
        ensure_status_tasks(application)
    else:
        touch_job_application(application)

    return task


def reopen_application_task(task):
    if task.completed_at:
        task.completed_at = None
        task.save(update_fields=["completed_at", "updated_at"])
        touch_job_application(task.job_application)

    return task


def ensure_interview_follow_up_task(event):
    if event.event_type != ApplicationEvent.EventType.INTERVIEW:
        return

    due_from = event.ends_at or event.starts_at

    create_auto_task(
        event.job_application,
        ApplicationTask.TaskType.INTERVIEW_FOLLOW_UP,
        {
            "title": "Send a follow-up email after the interview",
            "description": "Thank them for their time, mention what interested you, and ask about next steps if appropriate.",
            "source_status": JobApplication.Status.INTERVIEWING,
            "due_at": due_from + timedelta(days=7),
            "is_required": False,
        },
    )


def handle_application_event_automation(event):
    application = event.job_application

    if (
        event.event_type == ApplicationEvent.EventType.INTERVIEW
        and application.status in [
            JobApplication.Status.FOUND,
            JobApplication.Status.APPLIED,
        ]
    ):
        application.status = JobApplication.Status.INTERVIEWING
        application.save(update_fields=["status", "updated_at"])

    ensure_status_tasks(application)
    ensure_interview_follow_up_task(event)
