from django.conf import settings
from django.db import models

class JobApplication(models.Model):
    class SourcePlatform(models.TextChoices):
        SEEK = 'SEEK', 'Seek'
        LINKEDIN = 'LINKEDIN', 'LinkedIn'
        INDEED = 'INDEED', 'Indeed'
        OTHER = 'OTHER', 'Other'
        NOT_SPECIFIED = '', 'Not specified'

    class Status(models.TextChoices):
        FOUND = 'FOUND', 'Found'
        APPLIED = 'APPLIED', 'Applied'
        INTERVIEWING = 'INTERVIEWING', 'Interviewing'
        OFFER = 'OFFER', 'Offer'
        REJECTED = 'REJECTED', 'Rejected'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    source_platform = models.CharField(
        max_length=20,
        choices=SourcePlatform.choices,
        blank=True,
        default=SourcePlatform.OTHER
    )
    source_details = models.CharField(max_length=255, blank=True)
    job_url = models.URLField(max_length=2000, blank=True)
    date_posted = models.DateField(null=True, blank=True)
    date_applied = models.DateField(null=True, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='AUD')
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FOUND)
    interest_level = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"
    
class ApplicationContact(models.Model):
    job_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_application.company_name}"

class ApplicationNote(models.Model):
    job_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    title = models.CharField(max_length=255, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.job_application.job_title}"


class ApplicationTask(models.Model):
    class TaskType(models.TextChoices):
        TAILOR_RESUME = "TAILOR_RESUME", "Tailor resume"
        COVER_LETTER = "COVER_LETTER", "Prepare cover letter"
        SUBMIT_APPLICATION = "SUBMIT_APPLICATION", "Submit application"
        FOLLOW_UP = "FOLLOW_UP", "Follow up"
        INTERVIEW_PREP = "INTERVIEW_PREP", "Prepare for interview"
        INTERVIEW_FOLLOW_UP = "INTERVIEW_FOLLOW_UP", "Interview follow-up"
        REJECTION_FEEDBACK = "REJECTION_FEEDBACK", "Ask for feedback"
        OFFER_REVIEW = "OFFER_REVIEW", "Review offer"
        CUSTOM = "CUSTOM", "Custom"

    job_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    task_type = models.CharField(
        max_length=40,
        choices=TaskType.choices,
        default=TaskType.CUSTOM,
    )
    source_status = models.CharField(
        max_length=20,
        choices=JobApplication.Status.choices,
        blank=True,
    )
    auto_created = models.BooleanField(default=False)
    is_required = models.BooleanField(default=True)
    triggers_status_change_to = models.CharField(
        max_length=20,
        choices=JobApplication.Status.choices,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["completed_at", "due_at", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job_application", "task_type"],
                condition=models.Q(auto_created=True),
                name="unique_auto_task_per_application_type",
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.job_application.job_title}"


class ApplicationEvent(models.Model):
    class EventType(models.TextChoices):
        INTERVIEW = "INTERVIEW", "Interview"
        CALL = "CALL", "Call"
        DEADLINE = "DEADLINE", "Deadline"
        OTHER = "OTHER", "Other"

    job_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=255)
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.INTERVIEW,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    meeting_link = models.URLField(max_length=2000, blank=True)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.title} - {self.job_application.job_title}"
