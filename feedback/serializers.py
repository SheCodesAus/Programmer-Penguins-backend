from rest_framework import serializers
from .models import FeedbackMessage


class FeedbackMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackMessage
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "message_type",
            "related_page",
            "page_url",
            "subject",
            "message",
            "consent_given",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_consent_given(self, value):
        if not value:
            raise serializers.ValidationError(
                "Consent is required before submitting the form."
            )
        return value