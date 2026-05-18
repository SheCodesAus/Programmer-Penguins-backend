from django.conf import settings
from django.db import models


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        ARTICLE = "ARTICLE", "Article"
        CHATGPT = "CHATGPT", "ChatGPT answer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources",
    )
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.ARTICLE,
    )
    title = models.CharField(max_length=255)
    source_name = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)
    published_at = models.DateField(null=True, blank=True)
    url = models.URLField(max_length=2000, blank=True)
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
