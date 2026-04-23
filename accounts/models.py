from django.conf import settings
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class GenderChoices(models.TextChoices):
    WOMAN = "woman", "Woman"
    MAN = "man", "Man"
    NON_BINARY = "non_binary", "Non-binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"
    SELF_DESCRIBE = "self_describe", "Self-describe"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    desired_role = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    phone = PhoneNumberField(blank=True)
    linkedin_url = models.URLField(blank=True)
    gender = models.CharField(
        max_length=30,
        choices=GenderChoices.choices,
        blank=True,
    )
    gender_self_described = models.CharField(max_length=100, blank=True)
    career_goal = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.email or self.user.username}"
