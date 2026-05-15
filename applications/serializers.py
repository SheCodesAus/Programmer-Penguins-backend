from datetime import timedelta

from rest_framework import serializers
from django.utils import timezone

from .models import (
    ApplicationContact,
    ApplicationEvent,
    ApplicationNote,
    ApplicationTask,
    JobApplication,
)


class JobApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_platform_display = serializers.CharField(
        source="get_source_platform_display",
        read_only=True,
    )
    source_platform = serializers.ChoiceField(
        choices=JobApplication.SourcePlatform.choices,
        required=False,
        allow_blank=True,
    )
    task_summary = serializers.SerializerMethodField()
    next_event = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "user",
            "job_title",
            "company_name",
            "source_platform",
            "source_platform_display",
            "source_details",
            "job_url",
            "date_posted",
            "date_applied",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "status",
            "status_display",
            "interest_level",
            "is_active",
            "is_archived",
            "archived_at",
            "created_at",
            "updated_at",
            "task_summary",
            "next_event",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "source_platform_display",
            "status_display",
            "is_archived",
            "archived_at",
            "task_summary",
            "next_event",
        ]

    def get_task_summary(self, obj):
        tasks = getattr(obj, "prefetched_tasks", None)

        if tasks is None:
            tasks = list(obj.tasks.all())

        open_tasks = [task for task in tasks if task.completed_at is None]
        required_open_tasks = [task for task in open_tasks if task.is_required]
        now = timezone.now()

        due_tasks = [task for task in open_tasks if task.due_at]
        next_task = min(due_tasks, key=lambda task: task.due_at, default=None)

        if next_task is None:
            next_task = min(open_tasks, key=lambda task: task.created_at, default=None)

        prep_task_types = [
            ApplicationTask.TaskType.TAILOR_RESUME,
            ApplicationTask.TaskType.COVER_LETTER,
        ]

        has_open_prep_tasks = any(
            task.task_type in prep_task_types and task.is_required
            for task in open_tasks
        )

        has_open_submit_task = any(
            task.task_type == ApplicationTask.TaskType.SUBMIT_APPLICATION
            for task in open_tasks
        )

        return {
            "open_count": len(open_tasks),
            "required_open_count": len(required_open_tasks),
            "overdue_count": len([
                task for task in open_tasks if task.due_at and task.due_at < now
            ]),
            "due_soon_count": len([
                task
                for task in open_tasks
                if task.due_at and now <= task.due_at <= now + timedelta(days=2)
            ]),
            "ready_to_apply": (
                obj.status == JobApplication.Status.FOUND
                and has_open_submit_task
                and not has_open_prep_tasks
            ),
            "next_task": (
                {
                    "id": next_task.id,
                    "title": next_task.title,
                    "due_at": next_task.due_at,
                    "task_type": next_task.task_type,
                }
                if next_task
                else None
            ),
        }

    def get_next_event(self, obj):
        upcoming_events = getattr(obj, "prefetched_upcoming_events", None)

        if upcoming_events is None:
            event = obj.events.filter(starts_at__gte=timezone.now()).order_by("starts_at").first()
        else:
            event = upcoming_events[0] if upcoming_events else None

        if not event:
            return None

        return {
            "id": event.id,
            "title": event.title,
            "event_type": event.event_type,
            "starts_at": event.starts_at,
            "ends_at": event.ends_at,
        }


class JobApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    source_platform = serializers.ChoiceField(
        choices=JobApplication.SourcePlatform.choices,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job_title",
            "company_name",
            "source_platform",
            "source_details",
            "job_url",
            "date_posted",
            "date_applied",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "status",
            "interest_level",
            "is_active",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = [
            "id",
            "archived_at",
        ]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")
        source_platform = attrs.get("source_platform", "")

        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {"salary_max": "salary_max must be greater than or equal to salary_min."}
            )

        if source_platform != JobApplication.SourcePlatform.OTHER:
            attrs["source_details"] = ""

        interest_level = attrs.get("interest_level")

        if interest_level is not None and (interest_level < 0 or interest_level > 3):
            raise serializers.ValidationError(
                {"interest_level": "Interest level must be between 0 and 3."}
            )

        return attrs
    
class ApplicationContactSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_application.job_title", read_only=True)
    company_name = serializers.CharField(source="job_application.company_name", read_only=True)
    application_status = serializers.CharField(source="job_application.status", read_only=True)
    application_status_display = serializers.CharField(
        source="job_application.get_status_display",
        read_only=True,
    )
    application_is_active = serializers.BooleanField(
        source="job_application.is_active",
        read_only=True,
    )
    application_is_archived = serializers.BooleanField(
        source="job_application.is_archived",
        read_only=True,
    )

    class Meta:
        model = ApplicationContact
        fields = [
            "id",
            "job_application",
            "job_title",
            "company_name",
            "application_status",
            "application_status_display",
            "application_is_active",
            "application_is_archived",
            "first_name",
            "last_name",
            "email",
            "phone",
            "note",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_application",
            "job_title",
            "company_name",
            "application_status",
            "application_status_display",
            "application_is_active",
            "application_is_archived",
            "created_at",
            "updated_at",
        ]
class ApplicationNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationNote
        fields = [
            "id",
            "job_application",
            "title",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_application",
            "created_at",
            "updated_at",
        ]


class ApplicationTaskSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_application.job_title", read_only=True)
    company_name = serializers.CharField(source="job_application.company_name", read_only=True)
    application_status = serializers.CharField(source="job_application.status", read_only=True)
    task_type_display = serializers.CharField(source="get_task_type_display", read_only=True)

    class Meta:
        model = ApplicationTask
        fields = [
            "id",
            "job_application",
            "job_title",
            "company_name",
            "application_status",
            "title",
            "description",
            "due_at",
            "completed_at",
            "task_type",
            "task_type_display",
            "source_status",
            "auto_created",
            "is_required",
            "triggers_status_change_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_title",
            "company_name",
            "application_status",
            "task_type_display",
            "completed_at",
            "auto_created",
            "created_at",
            "updated_at",
        ]

    def validate_job_application(self, value):
        request = self.context.get("request")

        if request and value.user != request.user:
            raise serializers.ValidationError("Invalid job application.")

        return value


class ApplicationEventSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job_application.job_title", read_only=True)
    company_name = serializers.CharField(source="job_application.company_name", read_only=True)
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)
    overlap_warning = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationEvent
        fields = [
            "id",
            "job_application",
            "job_title",
            "company_name",
            "title",
            "event_type",
            "event_type_display",
            "starts_at",
            "ends_at",
            "location",
            "meeting_link",
            "contact_name",
            "contact_email",
            "contact_phone",
            "notes",
            "overlap_warning",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job_title",
            "company_name",
            "event_type_display",
            "overlap_warning",
            "created_at",
            "updated_at",
        ]

    def validate_job_application(self, value):
        request = self.context.get("request")

        if request and value.user != request.user:
            raise serializers.ValidationError("Invalid job application.")

        return value

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))

        if ends_at and starts_at and ends_at <= starts_at:
            raise serializers.ValidationError({
                "ends_at": "End time must be after start time."
            })

        return attrs

    def get_overlap_warning(self, obj):
        starts_at = obj.starts_at
        ends_at = obj.ends_at or obj.starts_at + timedelta(hours=1)

        overlapping_events = ApplicationEvent.objects.filter(
            job_application__user=obj.job_application.user,
            starts_at__lt=ends_at,
        ).exclude(id=obj.id)

        overlapping_events = [
            event
            for event in overlapping_events
            if (event.ends_at or event.starts_at + timedelta(hours=1)) > starts_at
        ]

        if not overlapping_events:
            return ""

        return "This event overlaps with another event."
