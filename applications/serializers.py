from rest_framework import serializers

from .models import JobApplication


class JobApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_platform_display = serializers.CharField(
        source="get_source_platform_display",
        read_only=True,
    )

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "user",
            "job_title",
            "company_name",
            "source_platform",
            "source_platform_display",
            "job_url",
            "date_posted",
            "date_applied",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "status",
            "status_display",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "source_platform_display",
            "status_display",
        ]


class JobApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            "job_title",
            "company_name",
            "source_platform",
            "job_url",
            "date_posted",
            "date_applied",
            "salary_min",
            "salary_max",
            "currency",
            "location",
            "status",
            "notes",
            "is_active",
        ]

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")

        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError(
                {"salary_max": "salary_max must be greater than or equal to salary_min."}
            )

        return attrs