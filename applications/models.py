from django.conf import settings
from django.db import models

class JobApplication(models.Model):
    class SourcePlatform(models.TextChoices):
        SEEK = 'SEEK', 'Seek'
        LINKEDIN = 'LINKEDIN', 'LinkedIn'
        INDEED = 'INDEED', 'Indeed'
        OTHER = 'OTHER', 'Other'

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
        default=SourcePlatform.OTHER
    )
    source_details = models.CharField(max_length=255, blank=True)
    job_url = models.URLField(blank=True)
    date_posted = models.DateField(null=True, blank=True)
    date_applied = models.DateField(null=True, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='AUD')
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FOUND)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"
