from django.conf import settings
from django.db import models


class FeedbackMessage(models.Model):
    class RelatedPage(models.TextChoices):
        DASHBOARD = "DASHBOARD", "Dashboard"
        JOB_APPLICATION = "JOB_APPLICATION", "Job Application"
        TASKS_EVENTS = "TASKS_EVENTS", "Tasks and Events"
        PROFILE = "PROFILE", "Profile"
        LOGIN_SIGNUP = "LOGIN_SIGNUP", "Login / Sign up"
        ACCOUNT_RECOVERY = "ACCOUNT_RECOVERY", "Account recovery"
        OTHER = "OTHER", "Other"

    class MessageType(models.TextChoices):
        BUG = "BUG", "Bug report"
        QUESTION = "QUESTION", "Question"
        ACCOUNT_RECOVERY = "ACCOUNT_RECOVERY", "Account recovery"
        SUGGESTION = "SUGGESTION", "Suggestion"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_messages",
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    message_type = models.CharField(
        max_length=30,
        choices=MessageType.choices,
        default=MessageType.QUESTION,
    )
    related_page = models.CharField(
        max_length=40,
        choices=RelatedPage.choices,
        default=RelatedPage.OTHER,
    )
    page_url = models.URLField(max_length=2000, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    consent_given = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.message_type}"