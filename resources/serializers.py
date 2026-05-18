from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    resource_type_display = serializers.CharField(source="get_resource_type_display", read_only=True)

    class Meta:
        model = Resource
        fields = [
            "id",
            "resource_type",
            "resource_type_display",
            "title",
            "source_name",
            "author",
            "published_at",
            "url",
            "question",
            "answer",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "resource_type_display", "created_at", "updated_at"]

    def validate(self, attrs):
        resource_type = attrs.get(
            "resource_type",
            getattr(self.instance, "resource_type", Resource.ResourceType.ARTICLE),
        )
        url = attrs.get("url", getattr(self.instance, "url", ""))
        answer = attrs.get("answer", getattr(self.instance, "answer", ""))

        if resource_type == Resource.ResourceType.ARTICLE and not url:
            raise serializers.ValidationError({"url": "A URL is required for article resources."})

        if resource_type == Resource.ResourceType.CHATGPT and not answer:
            raise serializers.ValidationError({"answer": "An answer is required for ChatGPT resources."})

        return attrs
